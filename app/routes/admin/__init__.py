from flask import Blueprint, url_for # Import url_for here

admin_bp = Blueprint('admin_portal', __name__, template_folder='../../templates/admin', url_prefix='/admin')

# A dummy admin class to provide the nested structure Flask-Admin templates expect
class DummyAdmin:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.name = "Admin Portal"
        self.base_template = None
        self.template_mode = None

# A dummy class to mock the admin_view context variable
class DummyAdminView:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        # Create the nested admin object that Flask-Admin templates expect
        self.admin = DummyAdmin(endpoint)
        # Add other attributes that might be accessed by the templates
        self.name = "Admin Portal"
        self.category = None
        self.menu_icon_type = None
        self.menu_icon_value = None

    def get_url(self, endpoint, **kwargs):
        # A basic implementation for get_url, assuming it might be called
        try:
            return url_for(endpoint, **kwargs)
        except: # noqa E722
            return "#" # Fallback URL

@admin_bp.context_processor
def inject_admin_view():
    def get_url(endpoint, **kwargs):
        """Mock get_url function for Flask-Admin templates"""
        try:
            return url_for(endpoint, **kwargs)
        except: # noqa E722
            return "#"  # Fallback URL
    
    return dict(
        admin_view=DummyAdminView(endpoint='admin_portal.index'),
        get_url=get_url
    )

from . import routes # noqa: E402, F401
