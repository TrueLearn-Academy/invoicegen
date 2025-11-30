from app.routes.dashboard import dashboard_bp
from app.routes.employees import employees_bp
from app.routes.invoices import invoices_bp
from app.routes.settings import settings_bp

def register_routes(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(settings_bp)

