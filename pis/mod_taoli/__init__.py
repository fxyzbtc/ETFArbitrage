from flask import Blueprint
from . import views

taoli_bp = Blueprint('taoli', __name__, url_prefix='/taoli', template_folder='templates', static_folder='static')
taoli_bp.add_url_rule('/', view_func=views.List.as_view('taoli_list'))
taoli_bp.add_url_rule('/update/', view_func=views.Update.as_view('taoli_update'))

taoli_bp.add_url_rule('/top/', view_func=views.Top.as_view('taoli_top'))
taoli_bp.add_url_rule('/updatetop/', view_func=views.UpdateTop.as_view('update_top'))