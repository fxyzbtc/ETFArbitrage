from flask import Blueprint
from . import views

pe_bp = Blueprint('pe', __name__, url_prefix='/pe', template_folder='templates', static_folder='static')
pe_bp.add_url_rule('/syncindice/', view_func=views.SyncIndice.as_view('sync_indice'))
pe_bp.add_url_rule('/syncpepb/<int:stockid>/', view_func=views.SyncPePb.as_view('sync_pepb'))

pe_bp.add_url_rule('/', view_func=views.ListIndice.as_view('list_indice'))
