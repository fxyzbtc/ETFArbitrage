from . import mail, db
from flask import render_template
from threading import Thread
from app import app
from flask_mail import Message
 
import datetime
 
def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)
 
 
def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thrd = Thread(target=async_send_mail, args=[app, msg])
    thrd.start()
    return thrd


def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
