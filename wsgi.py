from flask import Flask
from config import Config
from app.models import db
from app.routes import register_routes

def create_app():
    import os
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Add custom Jinja2 filter for nl2br
    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to <br> tags"""
        if value:
            return value.replace('\n', '<br>')
        return value
    
    # Register routes
    register_routes(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Initialize default company settings if not exists
        from app.models.company_settings import CompanySettings
        if not CompanySettings.query.first():
            default_settings = CompanySettings(
                company_name="TRUEZEN TECHNOLOGIES",
                company_address=""
            )
            db.session.add(default_settings)
            db.session.commit()
    
    return app

# Create app instance for Gunicorn (required for Render)
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for Render and other platforms)
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

