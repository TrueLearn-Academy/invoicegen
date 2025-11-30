from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.models import db
from app.models.employee import Employee
from decimal import Decimal
from datetime import datetime

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/')
def list_employees():
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    return render_template('employees.html', employees=employees)

@employees_bp.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            salary_per_annum = Decimal(request.form.get('salary_per_annum', 0))
            client_consultancy = request.form.get('client_consultancy')
            is_new_employee = request.form.get('is_new_employee') == 'on'
            date_of_joining_str = request.form.get('date_of_joining')
            salary_date = int(request.form.get('salary_date', 10))
            
            if not name or not client_consultancy:
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('employees.add_employee'))
            
            # Auto-calculate monthly salary
            salary_per_month = salary_per_annum / 12
            
            # Parse date of joining
            date_of_joining = None
            if date_of_joining_str:
                try:
                    date_of_joining = datetime.strptime(date_of_joining_str, '%Y-%m-%d').date()
                except ValueError:
                    date_of_joining = None
            
            employee = Employee(
                name=name,
                salary_per_annum=salary_per_annum,
                salary_per_month=salary_per_month,
                client_consultancy=client_consultancy,
                is_new_employee=is_new_employee,
                date_of_joining=date_of_joining,
                salary_date=salary_date
            )
            
            db.session.add(employee)
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('employees.list_employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
            return redirect(url_for('employees.add_employee'))
    
    return render_template('employees.html', action='add')

@employees_bp.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('employees.list_employees'))

@employees_bp.route('/api/by-consultancy/<consultancy>')
def get_employees_by_consultancy(consultancy):
    employees = Employee.query.filter_by(client_consultancy=consultancy).all()
    return jsonify([emp.to_dict() for emp in employees])

