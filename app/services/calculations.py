"""
Helper functions for invoice calculations including pro-rated salary and PF
"""
from decimal import Decimal
from datetime import date, datetime
from calendar import monthrange

def calculate_pro_rated_salary(employee, invoice_date):
    """
    Calculate pro-rated salary based on date of joining.
    For new employees: Always calculates from joining date to end of joining month.
    Logic:
    - If employee is new and invoice is within 1 month of joining: calculate pro-rated for joining month
    - If invoice is for the joining month: calculate pro-rated from joining date to end of month
    - If invoice is for a month AFTER joining: full salary (they worked full month)
    - If employee joined on 1st of month: full salary for that month
    - If no date of joining: full monthly salary
    """
    if not employee.date_of_joining:
        return Decimal(str(employee.salary_per_month))
    
    # Convert invoice_date to date if it's a datetime
    if isinstance(invoice_date, datetime):
        invoice_date = invoice_date.date()
    
    # Check if invoice is for the joining month (same year and month)
    is_joining_month = (employee.date_of_joining.year == invoice_date.year and 
                        employee.date_of_joining.month == invoice_date.month)
    
    # For new employees: if invoice is within 1 month of joining, calculate for joining month
    if employee.is_new_employee:
        # Calculate the end of joining month
        joining_month_end = date(employee.date_of_joining.year, employee.date_of_joining.month, 
                                monthrange(employee.date_of_joining.year, employee.date_of_joining.month)[1])
        
        # Calculate first day of month after joining
        if employee.date_of_joining.month == 12:
            next_month_start = date(employee.date_of_joining.year + 1, 1, 1)
        else:
            next_month_start = date(employee.date_of_joining.year, employee.date_of_joining.month + 1, 1)
        
        # If invoice date is within the joining month or the month after, calculate for joining month
        if invoice_date <= next_month_start or is_joining_month:
            # Calculate pro-rated for joining month
            if employee.date_of_joining.day == 1:
                return Decimal(str(employee.salary_per_month))
            
            days_in_month = monthrange(employee.date_of_joining.year, employee.date_of_joining.month)[1]
            days_worked = days_in_month - employee.date_of_joining.day + 1
            
            if days_worked <= 0:
                days_worked = 1
            if days_worked > days_in_month:
                days_worked = days_in_month
            
            monthly_salary = Decimal(str(employee.salary_per_month))
            daily_rate = monthly_salary / Decimal(days_in_month)
            pro_rated = daily_rate * Decimal(days_worked)
            pro_rated = pro_rated.quantize(Decimal('0.01'))
            
            return pro_rated
    
    # If invoice is for the joining month, calculate pro-rated salary
    if is_joining_month:
        # If joined on 1st of month, full salary
        if employee.date_of_joining.day == 1:
            return Decimal(str(employee.salary_per_month))
        
        # Calculate days in the joining month
        days_in_month = monthrange(employee.date_of_joining.year, employee.date_of_joining.month)[1]
        
        # Calculate days worked (from joining date to end of month, inclusive)
        # Example: Joined Nov 11, days_in_month = 30, days_worked = 30 - 11 + 1 = 20 days
        days_worked = days_in_month - employee.date_of_joining.day + 1
        
        # Ensure days_worked is positive and not more than days in month
        if days_worked <= 0:
            days_worked = 1
        if days_worked > days_in_month:
            days_worked = days_in_month
        
        # Pro-rated salary = (monthly_salary / days_in_month) * days_worked
        monthly_salary = Decimal(str(employee.salary_per_month))
        daily_rate = monthly_salary / Decimal(days_in_month)
        pro_rated = daily_rate * Decimal(days_worked)
        
        # Round to 2 decimal places
        pro_rated = pro_rated.quantize(Decimal('0.01'))
        
        return pro_rated
    
    # If invoice is for a month AFTER the joining month, employee worked full month
    elif (employee.date_of_joining.year < invoice_date.year or 
          (employee.date_of_joining.year == invoice_date.year and 
           employee.date_of_joining.month < invoice_date.month)):
        # Employee joined in a previous month, they worked full month for this invoice
        return Decimal(str(employee.salary_per_month))
    
    # If invoice is for a month BEFORE joining (shouldn't happen, but handle it)
    else:
        return Decimal('0')

def calculate_pf(amount, pf_percentage=12):
    """
    Calculate PF (Provident Fund) - default is 12% in India
    Returns both employee PF and employer PF (both are same percentage)
    """
    pf_decimal = Decimal(str(pf_percentage)) / Decimal('100')
    pf_amount = amount * pf_decimal
    return pf_amount, pf_amount  # Employee PF, Employer PF

def calculate_employee_totals(employee, invoice_date):
    """
    Calculate all amounts for an employee:
    - Pro-rated salary (based on working days)
    - Employee PF (fixed 1440) - paid by consultancy
    - Employer PF (fixed 1440) - paid by consultancy
    - Total cost (salary + employee PF + employer PF) - all paid by consultancy
    """
    pro_rated_salary = calculate_pro_rated_salary(employee, invoice_date)
    # Fixed PF amounts for both employee and employer
    employee_pf = Decimal('1440')
    employer_pf = Decimal('1440')
    # Total cost includes all: salary + employee PF + employer PF (all paid by consultancy)
    total_cost = pro_rated_salary + employee_pf + employer_pf
    
    return {
        'pro_rated_salary': pro_rated_salary,
        'employee_pf': employee_pf,
        'employer_pf': employer_pf,
        'total_cost': total_cost
    }

def format_currency_inr(amount):
    """Format amount as Indian Rupees - using INR symbol that displays correctly"""
    # Use 'INR' or 'Rs.' if ₹ doesn't render properly
    return f"INR {float(amount):,.2f}"

