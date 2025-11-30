"""
Database migration script to add new fields to employees table:
- is_new_employee (boolean, default False)
- date_of_joining (date, nullable)
- salary_date (integer, default 10)
"""
from flask import Flask
from config import Config
from app.models import db
from app.models.employee import Employee

def migrate_employee_fields():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if columns exist
            columns_to_add = []
            
            # Check is_new_employee
            try:
                db.session.execute(db.text("SELECT is_new_employee FROM employees LIMIT 1"))
                print("✓ is_new_employee column already exists")
            except Exception:
                columns_to_add.append(("is_new_employee", "BOOLEAN DEFAULT 0"))
            
            # Check date_of_joining
            try:
                db.session.execute(db.text("SELECT date_of_joining FROM employees LIMIT 1"))
                print("✓ date_of_joining column already exists")
            except Exception:
                columns_to_add.append(("date_of_joining", "DATE"))
            
            # Check salary_date
            try:
                db.session.execute(db.text("SELECT salary_date FROM employees LIMIT 1"))
                print("✓ salary_date column already exists")
            except Exception:
                columns_to_add.append(("salary_date", "INTEGER DEFAULT 10"))
            
            # Add missing columns
            if columns_to_add:
                for col_name, col_def in columns_to_add:
                    print(f"Adding {col_name} column to employees table...")
                    db.session.execute(db.text(f"ALTER TABLE employees ADD COLUMN {col_name} {col_def}"))
                    db.session.commit()
                    print(f"✓ {col_name} column added successfully")
                
                # Update existing records to have default salary_date if it's NULL
                db.session.execute(db.text("UPDATE employees SET salary_date = 10 WHERE salary_date IS NULL"))
                db.session.commit()
                print("✓ Updated existing records with default salary_date")
            else:
                print("All columns already exist. No migration needed.")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            # Try alternative: drop and recreate
            print("Attempting to recreate table...")
            try:
                db.drop_all()
                db.create_all()
                print("✓ Database recreated successfully")
            except Exception as e2:
                print(f"Error recreating database: {e2}")

if __name__ == '__main__':
    migrate_employee_fields()
    print("Migration complete!")

