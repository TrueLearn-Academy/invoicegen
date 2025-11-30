from app.models import db
from datetime import date

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    salary_per_annum = db.Column(db.Numeric(10, 2), nullable=False)
    salary_per_month = db.Column(db.Numeric(10, 2), nullable=False)
    client_consultancy = db.Column(db.String(200), nullable=False)
    is_new_employee = db.Column(db.Boolean, default=False, nullable=False)
    date_of_joining = db.Column(db.Date, nullable=True)
    salary_date = db.Column(db.Integer, default=10, nullable=False)  # Day of month (default 10th)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'salary_per_annum': float(self.salary_per_annum),
            'salary_per_month': float(self.salary_per_month),
            'client_consultancy': self.client_consultancy,
            'is_new_employee': self.is_new_employee,
            'date_of_joining': self.date_of_joining.strftime('%Y-%m-%d') if self.date_of_joining else None,
            'salary_date': self.salary_date
        }

