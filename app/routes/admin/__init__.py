from flask import Blueprint, url_for

admin_bp = Blueprint('admin_portal', __name__, template_folder='../../templates/admin', url_prefix='/admin')

class AdminTemplateShim:
    """Expose the minimal Flask-Admin attributes required by the templates."""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.name = "Admin Portal"
        self.base_template = None
        self.template_mode = None

class AdminViewShim:
    """Provide template-safe admin view metadata without a full Flask-Admin instance."""

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.admin = AdminTemplateShim(endpoint)
        self.name = "Admin Portal"
        self.category = None
        self.menu_icon_type = None
        self.menu_icon_value = None

    def get_url(self, endpoint, **kwargs):
        try:
            return url_for(endpoint, **kwargs)
        except Exception:
            return "#"

@admin_bp.context_processor
def inject_admin_view():
    def get_url(endpoint, **kwargs):
        """Resolve admin template URLs without requiring Flask-Admin globals."""
        try:
            return url_for(endpoint, **kwargs)
        except Exception:
            return "#"
    
    return dict(
        admin_view=AdminViewShim(endpoint='admin_portal.index'),
        get_url=get_url
    )

from . import routes  # noqa: E402, F401
