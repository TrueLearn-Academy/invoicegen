"""
Database migration script to add miscellaneous_cost column to invoices table
"""
from flask import Flask
from config import Config
from app.models import db
from app.models.invoice import Invoice

def migrate_invoice_miscellaneous():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column exists
            try:
                db.session.execute(db.text("SELECT miscellaneous_cost FROM invoices LIMIT 1"))
                print("✓ miscellaneous_cost column already exists")
            except Exception:
                # Column doesn't exist, add it
                print("Adding miscellaneous_cost column to invoices table...")
                db.session.execute(db.text("ALTER TABLE invoices ADD COLUMN miscellaneous_cost NUMERIC(10, 2) DEFAULT 0"))
                db.session.commit()
                print("✓ miscellaneous_cost column added successfully")
                
                # Update existing records to have default value
                db.session.execute(db.text("UPDATE invoices SET miscellaneous_cost = 0 WHERE miscellaneous_cost IS NULL"))
                db.session.commit()
                print("✓ Updated existing records with default miscellaneous_cost")
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_invoice_miscellaneous()
    print("Migration complete!")

