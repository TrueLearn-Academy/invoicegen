# Auto Invoice Generator

A production-ready full-stack web application for generating payroll invoices for clients/consultancies with one click.

## Features

- **Employee Management**: Add, view, and delete employees with salary information
- **Invoice Generation**: Generate invoices with automatic calculations
- **PDF Export**: Export invoices as PDF files
- **Invoice History**: View and manage previous invoices
- **Company Settings**: Configure company address and details

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
/app
  /models
    - employee.py
    - invoice.py
    - company_settings.py
  /routes
    - __init__.py
    - dashboard.py
    - employees.py
    - invoices.py
    - settings.py
  /services
    - pdf_service.py
  /templates
    - base.html
    - dashboard.html
    - employees.html
    - invoice_generate.html
    - invoice_history.html
    - invoice_detail.html
    - settings.html
  /static
    - css/style.css
  config.py
  app.py
```

## Usage

1. **Company Settings**: First, configure your company address in the Company Settings page
2. **Add Employees**: Add employees with their salary information and associated client/consultancy
3. **Generate Invoice**: Select a client/consultancy and employees to generate an invoice
4. **Export PDF**: Download invoices as PDF files
5. **View History**: Access previous invoices from the Invoice History page

## Database

The application uses SQLite database (`invoices.db`) which is automatically created on first run.

## Technologies

- Flask 3.0.0
- SQLAlchemy 2.0.36
- Flask-SQLAlchemy 3.1.1
- ReportLab 4.0.4 (for PDF generation)
- Bootstrap 5
- Jinja2 Templates

## Sample Invoice Preview

A sample invoice preview is available in `sample_invoice_preview.html`. Open this file in your browser to see how generated invoices will look.

