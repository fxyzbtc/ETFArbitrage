from flask import Blueprint
from . import views

mail_bp = Blueprint('mail', __name__, url_prefix='/mail', template_folder='templates', static_folder='static')
mail_bp.add_url_rule('/notify/', view_func=views.NotifyAll.as_view('mail_notify'))
mail_bp.add_url_rule('/subscribe/', view_func=views.Subscribe.as_view('mail_subscribe'))
