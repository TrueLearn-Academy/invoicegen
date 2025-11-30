from app.models import db

class CompanySettings(db.Model):
    __tablename__ = 'company_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False, default="TRUEZEN TECHNOLOGIES")
    company_address = db.Column(db.Text, nullable=False, default="")
    logo_path = db.Column(db.String(500), nullable=True, default=None)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<CompanySettings {self.company_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_address': self.company_address,
            'logo_path': self.logo_path
        }

