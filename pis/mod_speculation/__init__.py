from flask import Blueprint
from . import views

spec_bp = Blueprint('spec', __name__, url_prefix='/spec', template_folder='templates', static_folder='static')
spec_bp.add_url_rule('/fund/', view_func=views.NewFund.as_view('newfund'))
#spec_bp.add_url_rule('/main/', view_func=views.MainForce.as_view('mainforce'))