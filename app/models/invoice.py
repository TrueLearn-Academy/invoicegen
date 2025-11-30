from app.models import db
import json

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    invoice_to = db.Column(db.String(200), nullable=False)
    client_consultancy = db.Column(db.String(200), nullable=False)
    employee_ids = db.Column(db.Text, nullable=False)  # JSON array of employee IDs
    total_monthly_payroll = db.Column(db.Numeric(10, 2), nullable=False)
    total_annual_payroll = db.Column(db.Numeric(10, 2), nullable=False)
    miscellaneous_cost = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    service_fee = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def get_employee_ids_list(self):
        return json.loads(self.employee_ids)
    
    def set_employee_ids_list(self, ids):
        self.employee_ids = json.dumps(ids)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'invoice_to': self.invoice_to,
            'client_consultancy': self.client_consultancy,
            'employee_ids': self.get_employee_ids_list(),
            'total_monthly_payroll': float(self.total_monthly_payroll),
            'total_annual_payroll': float(self.total_annual_payroll),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

