from flask import Blueprint
from flask.views import View

class Home(View):
    def dispatch_request(self):
        return 'home'

