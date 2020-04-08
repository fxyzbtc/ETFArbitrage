# -*- coding: utf-8 -*-

from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, render_template)
from flask_mail import Mail
import config

# initializes extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

# create application instance
app = Flask(__name__)
app.config.from_object(config)

#for deveopment only
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

db.init_app(app)
mail.init_app(app)
migrate.init_app(app, db)

#otherviews
from .mod_taoli import taoli_bp
app.register_blueprint(taoli_bp)
from .mod_pe import pe_bp
app.register_blueprint(pe_bp)
from .mod_speculation import spec_bp
app.register_blueprint(spec_bp)

from .mod_mail import mail_bp
app.register_blueprint(mail_bp)

#main views
from flask import Blueprint
from flask import render_template
from . import views

main_bp = Blueprint('main', __name__, url_prefix='/', template_folder='templates', static_folder='static')
main_bp.add_url_rule('/', view_func=views.Home.as_view('main'))
app.register_blueprint(main_bp)



# import models
from .mod_pe.models import PePb
from .mod_pe.models import Indice
from .mod_taoli.models import Discount
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500

