"""
Database migration script to add service_fee column to invoices table
"""
from flask import Flask
from config import Config
from app.models import db
from app.models.invoice import Invoice

def migrate_invoice_service_fee():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column exists
            try:
                db.session.execute(db.text("SELECT service_fee FROM invoices LIMIT 1"))
                print("✓ service_fee column already exists")
            except Exception:
                # Column doesn't exist, add it
                print("Adding service_fee column to invoices table...")
                db.session.execute(db.text("ALTER TABLE invoices ADD COLUMN service_fee NUMERIC(10, 2) DEFAULT 0"))
                db.session.commit()
                print("✓ service_fee column added successfully")
                
                # Update existing records to have default value
                db.session.execute(db.text("UPDATE invoices SET service_fee = 0 WHERE service_fee IS NULL"))
                db.session.commit()
                print("✓ Updated existing records with default service_fee")
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_invoice_service_fee()
    print("Migration complete!")

