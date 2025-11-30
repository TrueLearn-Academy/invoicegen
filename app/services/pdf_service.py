from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER
from flask import current_app
import tempfile
from decimal import Decimal
import os
from config import Config
from app.services.calculations import calculate_employee_totals, format_currency_inr

def generate_pdf(invoice, employees, company_settings):
    """Generate PDF from invoice data using ReportLab"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(temp_file.name, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Section heading style
    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        spaceAfter=4,
    )
    
    normal_style = styles['Normal']
    right_style = ParagraphStyle(
        'RightAlign',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
    )
    
    # Small text style for contact info
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
    )
    
    # Calculate full width to match table (same as employee table width)
    full_width = 8*inch  # 4 + 2 + 2 inches for the three columns
    
    # Header - Traditional invoice format
    # Top section: Company info (left) and INVOICE title (right)
    
    # Add logo if exists (check root folder first, then company_settings)
    logo_image = None
    logo_paths = [
        os.path.join(Config.BASE_DIR, 'logo.png'),  # Check root folder first
    ]
    
    # Also check company_settings.logo_path if it exists
    if company_settings.logo_path:
        logo_paths.append(os.path.join(Config.BASE_DIR, 'app', 'static', company_settings.logo_path))
    
    for logo_full_path in logo_paths:
        if os.path.exists(logo_full_path):
            try:
                # Create image with larger size
                logo_image = Image(logo_full_path, width=7.65*inch, height=1.77*inch, kind='proportional')
                break  # Use first found logo
            except Exception as e:
                # If image loading fails, try next path
                continue
    
    # Build header with logo on left and invoice details on right, all on same line
    # Create invoice details (number and date) on right side
    invoice_number_para = Paragraph(f"INVOICE #{invoice.invoice_number}", right_style)
    invoice_date_para = Paragraph(f"DATE: {invoice.invoice_date.strftime('%d %B %Y').upper()}", right_style)
    
    # Create a table with logo on left and invoice details on right
    header_data = []
    if logo_image:
        # Logo on left, invoice details on right
        invoice_details_cell = Table([
            [invoice_number_para],
            [invoice_date_para]
        ], colWidths=[3.2*inch])
        invoice_details_cell.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        header_data.append([logo_image, invoice_details_cell])
    else:
        # No logo, just invoice details
        invoice_details_cell = Table([
            [invoice_number_para],
            [invoice_date_para]
        ], colWidths=[8*inch])
        invoice_details_cell.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        header_data.append([Paragraph("", normal_style), invoice_details_cell])
    
    # Header table with logo and invoice details on same line
    header_table = Table(header_data, colWidths=[4.8*inch, 3.2*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, -1), -3),  # Negative padding to move logo left
        ('LEFTPADDING', (1, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    
    # Add company address and contact info below logo (left aligned)
    elements.append(Spacer(1, 0.05*inch))
    
    # Company address - below logo, left aligned, starting from left edge
    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        alignment=TA_LEFT,
        leftIndent=0,  # Start from left edge
    )
    address_text = company_settings.company_address if company_settings.company_address else "Nyanapahalli Main Rd, Maruthi Layout, Royal Shelters, Stage 4, Bommanahalli, Bengaluru, Karnataka 560068"
    for line in address_text.split('\n'):
        if line.strip():
            elements.append(Paragraph(line.strip(), address_style))
    
    # Email and phone - left aligned, starting from left edge
    elements.append(Paragraph("Email: payroll@truezentechnologies.com", address_style))
    elements.append(Paragraph("Phone: 9986553505", address_style))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # TO section - highlighted with larger font, client name on single line
    to_heading_style = ParagraphStyle(
        'TOHeading',
        parent=styles['Normal'],
        fontSize=13,
        fontName='Helvetica-Bold',
        textColor=colors.black,
        spaceAfter=6,
    )
    to_content_style = ParagraphStyle(
        'TOContent',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica',
        textColor=colors.black,
        spaceAfter=0,
        wordWrap='CJK',  # Prevent word wrapping to keep on single line
        allowWidows=0,
        allowOrphans=0,
    )
    # Replace spaces with non-breaking spaces to keep client name on one line
    client_name_single_line = invoice.invoice_to.replace(' ', '\u00A0')
    to_data = [
        [Paragraph("<b>TO:</b>", to_heading_style)],
        [Paragraph(client_name_single_line, to_content_style)]
    ]
    to_table = Table(to_data, colWidths=[full_width])
    to_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),  # No left padding - starts from left edge
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),  # Light grey background for highlighting
    ]))
    elements.append(to_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Define bold style for total row
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
    )
    
    # Calculate employee totals
    employee_calculations = []
    total_salary = Decimal('0')
    total_employee_pf = Decimal('0')
    total_employer_pf = Decimal('0')
    
    for employee in employees:
        calc = calculate_employee_totals(employee, invoice.invoice_date)
        employee_calculations.append({
            'employee': employee,
            'calc': calc
        })
        total_salary += calc['pro_rated_salary']
        total_employee_pf += calc['employee_pf']
        total_employer_pf += calc['employer_pf']
    
    # Table data - header row with PF columns
    table_data = [[
        'EMPLOYEE NAME',
        'PRO-RATED SALARY',
        'EMPLOYEE PF (12%)',
        'EMPLOYER PF (12%)',
        'TOTAL COST'
    ]]
    
    # Employee rows with calculations
    for item in employee_calculations:
        employee = item['employee']
        calc = item['calc']
        
        # Build description with employee name and additional info
        description_parts = [f"<b>{employee.name}</b>"]
        
        if employee.is_new_employee:
            new_emp_info = "New Employee"
            if employee.date_of_joining:
                new_emp_info += f" | Date of Joining: {employee.date_of_joining.strftime('%B %d, %Y')}"
            description_parts.append(f"<font size='6' color='#666666'>{new_emp_info}</font>")
        
        # Add salary date info
        salary_date_suffix = "th"
        if employee.salary_date == 1:
            salary_date_suffix = "st"
        elif employee.salary_date == 2:
            salary_date_suffix = "nd"
        elif employee.salary_date == 3:
            salary_date_suffix = "rd"
        
        salary_date_info = f"Salary Date: {employee.salary_date}{salary_date_suffix} of every month"
        description_parts.append(f"<font size='6' color='#666666'>{salary_date_info}</font>")
        
        description_text = "<br/>".join(description_parts)
        
        table_data.append([
            Paragraph(description_text, normal_style),
            format_currency_inr(calc['pro_rated_salary']),
            format_currency_inr(calc['employee_pf']),
            format_currency_inr(calc['employer_pf']),
            format_currency_inr(calc['total_cost'])
        ])
    
    # Sub-total row (salary + employee PF + employer PF)
    table_data.append([
        'SUB-TOTAL',
        format_currency_inr(total_salary),
        format_currency_inr(total_employee_pf),
        format_currency_inr(total_employer_pf),
        format_currency_inr(total_salary + total_employee_pf + total_employer_pf)
    ])
    
    # Create table with simple, formal styling - proper grid with vertical lines
    employee_table = Table(table_data, colWidths=[3.0*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.0*inch])
    employee_table.setStyle(TableStyle([
        # Header row - simple bold text
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, 0), 10),
        ('RIGHTPADDING', (0, 0), (-1, 0), 10),
        # Line below header
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        # Data rows
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('TOPPADDING', (0, 1), (-1, -2), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 10),
        ('LEFTPADDING', (0, 1), (-1, -2), 10),
        ('RIGHTPADDING', (0, 1), (-1, -2), 10),
        ('ALIGN', (1, 1), (4, -2), 'RIGHT'),
        # Lines between data rows
        ('LINEBELOW', (0, 1), (-1, -2), 1, colors.black),
        # Total row - bold text, font size 7px
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 7),
        ('ALIGN', (1, -1), (4, -1), 'RIGHT'),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('LEFTPADDING', (0, -1), (-1, -1), 10),
        ('RIGHTPADDING', (0, -1), (-1, -1), 10),
        # Line above total row
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        # Vertical grid lines for columns
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        # Outer border
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(employee_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Miscellaneous costs section - left aligned
    miscellaneous_cost = invoice.miscellaneous_cost or Decimal('0')
    if miscellaneous_cost > 0:
        misc_style = ParagraphStyle('MiscStyle', parent=styles['Normal'], 
            fontSize=11, textColor=colors.black, alignment=TA_LEFT)
        misc_para = Paragraph(f"Miscellaneous Cost: {format_currency_inr(miscellaneous_cost)}", misc_style)
        elements.append(misc_para)
        elements.append(Spacer(1, 0.2*inch))
    
    # Service fee section - formatted as table for better alignment
    service_fee = invoice.service_fee or Decimal('0')
    if service_fee > 0:
        # Calculate base and GST from total service fee
        service_fee_base = service_fee / Decimal('1.18')
        service_fee_base = service_fee_base.quantize(Decimal('0.01'))
        service_fee_gst = service_fee - service_fee_base
        service_fee_gst = service_fee_gst.quantize(Decimal('0.01'))
        
        # Create service fee table for proper alignment - match employee table width
        service_fee_data = [
            [Paragraph("<b>Service Fee:</b>", ParagraphStyle('ServiceTitle', parent=styles['Normal'], 
                fontSize=11, fontName='Helvetica-Bold', alignment=TA_LEFT)), 
             Paragraph("", normal_style)],
            [Paragraph("Base Service Fee (INR 6,250 per employee)", ParagraphStyle('ServiceText', parent=styles['Normal'], 
                fontSize=10, alignment=TA_LEFT)),
             Paragraph(format_currency_inr(service_fee_base), ParagraphStyle('ServiceAmount', parent=styles['Normal'], 
                fontSize=10, alignment=TA_RIGHT))],
            [Paragraph("GST (18%)", ParagraphStyle('ServiceText', parent=styles['Normal'], 
                fontSize=10, alignment=TA_LEFT)),
             Paragraph(format_currency_inr(service_fee_gst), ParagraphStyle('ServiceAmount', parent=styles['Normal'], 
                fontSize=10, alignment=TA_RIGHT))],
            [Paragraph("<b>Total Service Fee</b>", ParagraphStyle('ServiceTotal', parent=styles['Normal'], 
                fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT)),
             Paragraph(f"<b>{format_currency_inr(service_fee)}</b>", ParagraphStyle('ServiceTotalAmount', parent=styles['Normal'], 
                fontSize=10, fontName='Helvetica-Bold', alignment=TA_RIGHT))]
        ]
        # Match the width of employee table (3.0 + 1.3 + 1.3 + 1.3 + 1.0 = 7.9 inches)
        service_fee_table = Table(service_fee_data, colWidths=[5.9*inch, 2.0*inch])
        service_fee_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, 2), 4),
            ('BOTTOMPADDING', (0, 1), (-1, 2), 4),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.HexColor('#ddd')),
            ('TOPPADDING', (0, 3), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 3), (-1, -1), 6),
        ]))
        elements.append(service_fee_table)
        elements.append(Spacer(1, 0.25*inch))
    
    # Grand Total: salary + employee PF + employer PF + miscellaneous + service fee
    grand_total = total_salary + total_employee_pf + total_employer_pf + miscellaneous_cost + service_fee
    grand_total_data = [
        [
            Paragraph("<b>GRAND TOTAL</b>", ParagraphStyle('GrandTotal', parent=styles['Normal'], 
                fontSize=12, fontName='Helvetica-Bold', alignment=TA_LEFT)),
            Paragraph(format_currency_inr(grand_total), ParagraphStyle('GrandTotalAmount', parent=styles['Normal'], 
                fontSize=12, fontName='Helvetica-Bold', alignment=TA_RIGHT))
        ]
    ]
    # Match the width of employee table for consistent alignment
    grand_total_table = Table(grand_total_data, colWidths=[5.9*inch, 2.0*inch])
    grand_total_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(grand_total_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Payment instructions (left side)
    if invoice.notes:
        payment_notes = Paragraph(
            invoice.notes,
            ParagraphStyle('PaymentNotes', parent=styles['Normal'], fontSize=9, 
                          textColor=colors.black, alignment=TA_LEFT)
        )
        elements.append(payment_notes)
        elements.append(Spacer(1, 0.2*inch))
    
    # Footer - Thank you message (centered, bold)
    elements.append(Spacer(1, 0.3*inch))
    thank_you = Paragraph(
        "<b>Thank you for your business!</b>",
        ParagraphStyle('ThankYou', parent=styles['Normal'], fontSize=12, 
                      fontName='Helvetica-Bold', textColor=colors.black, alignment=TA_CENTER)
    )
    elements.append(thank_you)
    
    # Disclaimer (centered, small, italic)
    elements.append(Spacer(1, 0.2*inch))
    disclaimer = Paragraph(
        "<i>This is a computer-generated invoice. No signature required.</i>",
        ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=9, 
                      textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(disclaimer)
    
    # Build PDF
    doc.build(elements)
    
    return temp_file.name

