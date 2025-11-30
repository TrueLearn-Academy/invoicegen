from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.employee import Employee
from app.models.invoice import Invoice
from app.models.company_settings import CompanySettings

