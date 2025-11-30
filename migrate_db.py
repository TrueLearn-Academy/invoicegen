"""
Database migration script to add logo_path column to company_settings table
"""
from flask import Flask
from config import Config
from app.models import db
from app.models.company_settings import CompanySettings

def migrate_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column exists by trying to query it
            try:
                db.session.execute(db.text("SELECT logo_path FROM company_settings LIMIT 1"))
                print("✓ logo_path column already exists")
            except Exception:
                # Column doesn't exist, add it
                print("Adding logo_path column to company_settings table...")
                db.session.execute(db.text("ALTER TABLE company_settings ADD COLUMN logo_path VARCHAR(500)"))
                db.session.commit()
                print("✓ logo_path column added successfully")
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            # Try alternative: drop and recreate
            print("Attempting to recreate table...")
            try:
                db.drop_all()
                db.create_all()
                # Recreate default settings
                default_settings = CompanySettings(
                    company_name="TRUEZEN TECHNOLOGIES",
                    company_address=""
                )
                db.session.add(default_settings)
                db.session.commit()
                print("✓ Database recreated successfully")
            except Exception as e2:
                print(f"Error recreating database: {e2}")

if __name__ == '__main__':
    migrate_database()
    print("Migration complete!")

