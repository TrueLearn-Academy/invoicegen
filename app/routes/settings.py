from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db
from app.models.company_settings import CompanySettings
import os
from werkzeug.utils import secure_filename
from config import Config

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@settings_bp.route('/', methods=['GET', 'POST'])
def company_settings():
    settings = CompanySettings.query.first()
    
    if not settings:
        settings = CompanySettings(
            company_name="TRUEZEN TECHNOLOGIES",
            company_address=""
        )
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            company_address = request.form.get('company_address', '')
            settings.company_address = company_address
            
            # Handle logo upload
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename and allowed_file(file.filename):
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(Config.BASE_DIR, 'app', 'static', 'uploads', 'logos')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    import time
                    filename = f"{int(time.time())}_{filename}"
                    filepath = os.path.join(upload_dir, filename)
                    file.save(filepath)
                    
                    # Store relative path
                    settings.logo_path = f"uploads/logos/{filename}"
                elif file and file.filename:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or SVG.', 'error')
            
            db.session.commit()
            flash('Company settings updated successfully!', 'success')
            return redirect(url_for('settings.company_settings'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'error')
            return redirect(url_for('settings.company_settings'))
    
    return render_template('settings.html', settings=settings)

