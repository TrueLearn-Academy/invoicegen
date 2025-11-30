from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, send_from_directory
from app.models import db
from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.company_settings import CompanySettings
from app.services.pdf_service import generate_pdf
from app.services.calculations import calculate_employee_totals, format_currency_inr
from decimal import Decimal
from datetime import date, datetime
import json
import os
from config import Config

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

@invoices_bp.route('/generate', methods=['GET', 'POST'])
def generate_invoice():
    if request.method == 'POST':
        try:
            client_consultancy = request.form.get('client_consultancy')
            invoice_to = request.form.get('invoice_to')
            employee_ids = request.form.getlist('employee_ids')
            include_service_fee = request.form.get('include_service_fee') == '1'
            miscellaneous_cost = Decimal(request.form.get('miscellaneous_cost', 0) or 0)
            notes = request.form.get('notes', '')
            
            if not client_consultancy or not invoice_to or not employee_ids:
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('invoices.generate_invoice'))
            
            # Get employees
            employees = Employee.query.filter(Employee.id.in_(employee_ids)).all()
            
            if not employees:
                flash('Please select at least one employee', 'error')
                return redirect(url_for('invoices.generate_invoice'))
            
            # Generate invoice number (ensure uniqueness)
            today = date.today()
            invoice_count = Invoice.query.filter(
                db.func.date(Invoice.created_at) == today
            ).count()
            
            # Try to generate unique invoice number
            max_attempts = 1000
            for attempt in range(max_attempts):
                invoice_number = f"INV-{today.strftime('%Y%m%d')}-{invoice_count + attempt + 1:03d}"
                # Check if this invoice number already exists
                existing = Invoice.query.filter_by(invoice_number=invoice_number).first()
                if not existing:
                    break
            else:
                # If we couldn't find a unique number, add timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%H%M%S')
                invoice_number = f"INV-{today.strftime('%Y%m%d')}-{timestamp}"
            
            # Calculate totals with pro-rated salary and PF
            total_monthly = Decimal('0')
            total_annual = Decimal('0')
            
            for emp in employees:
                # For monthly payroll calculation, use pro-rated if applicable
                emp_totals = calculate_employee_totals(emp, today)
                total_monthly += emp_totals['total_cost']  # Salary + Employer PF
                total_annual += Decimal(str(emp.salary_per_annum))
            
            # Calculate service fee: ₹6,250 per employee + 18% GST
            service_fee = Decimal('0')
            if include_service_fee:
                base_service_fee_per_employee = Decimal('6250')
                gst_percentage = Decimal('18')
                num_employees = len(employees)
                
                # Base service fee for all employees
                base_service_fee = base_service_fee_per_employee * Decimal(str(num_employees))
                # GST = 18% of base service fee
                gst_amount = (base_service_fee * gst_percentage) / Decimal('100')
                # Total service fee = base + GST
                service_fee = base_service_fee + gst_amount
                service_fee = service_fee.quantize(Decimal('0.01'))
            
            # Add miscellaneous cost and service fee to total
            total_monthly += miscellaneous_cost + service_fee
            
            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_number,
                invoice_date=today,
                invoice_to=invoice_to,
                client_consultancy=client_consultancy,
                employee_ids=json.dumps(employee_ids),
                total_monthly_payroll=total_monthly,
                total_annual_payroll=total_annual,
                miscellaneous_cost=miscellaneous_cost,
                service_fee=service_fee,
                notes=notes
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            flash('Invoice generated successfully!', 'success')
            return redirect(url_for('invoices.view_invoice', invoice_id=invoice.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating invoice: {str(e)}', 'error')
            return redirect(url_for('invoices.generate_invoice'))
    
    # GET request - show form
    employees = Employee.query.order_by(Employee.client_consultancy, Employee.name).all()
    employees_dict = [emp.to_dict() for emp in employees]
    consultancies = db.session.query(Employee.client_consultancy).distinct().all()
    consultancies = [c[0] for c in consultancies]
    
    return render_template('invoice_generate.html', 
                         employees=employees_dict, 
                         consultancies=consultancies)

@invoices_bp.route('/history')
def invoice_history():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('invoice_history.html', invoices=invoices)

@invoices_bp.route('/view/<int:invoice_id>')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    employee_ids = invoice.get_employee_ids_list()
    employees = Employee.query.filter(Employee.id.in_(employee_ids)).all()
    company_settings = CompanySettings.query.first()
    
    # Calculate employee details with PF and pro-rated salary
    employee_calculations = []
    total_salary = Decimal('0')
    total_employee_pf = Decimal('0')
    total_employer_pf = Decimal('0')
    
    for emp in employees:
        calc = calculate_employee_totals(emp, invoice.invoice_date)
        employee_calculations.append({
            'employee': emp,
            'pro_rated_salary': calc['pro_rated_salary'],
            'employee_pf': calc['employee_pf'],
            'employer_pf': calc['employer_pf'],
            'total_cost': calc['total_cost']
        })
        total_salary += calc['pro_rated_salary']
        total_employee_pf += calc['employee_pf']
        total_employer_pf += calc['employer_pf']
    
    # Calculate service fee breakdown
    service_fee = invoice.service_fee or Decimal('0')
    service_fee_base = Decimal('0')
    service_fee_gst = Decimal('0')
    if service_fee > 0:
        # Calculate base and GST from total service fee
        # If service_fee = base + (base * 0.18), then base = service_fee / 1.18
        service_fee_base = service_fee / Decimal('1.18')
        service_fee_base = service_fee_base.quantize(Decimal('0.01'))
        service_fee_gst = service_fee - service_fee_base
        service_fee_gst = service_fee_gst.quantize(Decimal('0.01'))
    
    # Calculate grand total: salary + employee PF + employer PF + miscellaneous + service fee
    grand_total = total_salary + total_employee_pf + total_employer_pf + (invoice.miscellaneous_cost or Decimal('0')) + service_fee
    
    return render_template('invoice_detail.html', 
                         invoice=invoice, 
                         employees=employees,
                         employee_calculations=employee_calculations,
                         total_salary=total_salary,
                         total_employee_pf=total_employee_pf,
                         total_employer_pf=total_employer_pf,
                         service_fee=service_fee,
                         service_fee_base=service_fee_base,
                         service_fee_gst=service_fee_gst,
                         grand_total=grand_total,
                         company_settings=company_settings)

@invoices_bp.route('/pdf/<int:invoice_id>')
def download_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    employee_ids = invoice.get_employee_ids_list()
    employees = Employee.query.filter(Employee.id.in_(employee_ids)).all()
    company_settings = CompanySettings.query.first()
    
    pdf_file = generate_pdf(invoice, employees, company_settings)
    
    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{invoice.invoice_number}.pdf"
    )

@invoices_bp.route('/api/consultancy/<consultancy>')
def get_employees_for_consultancy(consultancy):
    employees = Employee.query.filter_by(client_consultancy=consultancy).all()
    return jsonify([emp.to_dict() for emp in employees])

@invoices_bp.route('/logo')
def serve_logo():
    """Serve logo from root folder"""
    logo_path = os.path.join(Config.BASE_DIR, 'logo.png')
    if os.path.exists(logo_path):
        return send_from_directory(Config.BASE_DIR, 'logo.png')
    return '', 404

