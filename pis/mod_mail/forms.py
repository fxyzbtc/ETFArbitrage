# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm

from wtforms.fields.html5 import EmailField
from wtforms.fields import StringField
from wtforms.fields import HiddenField
from wtforms.fields import DateTimeField
from wtforms_components import TimeField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from datetime import datetime
import time
# class timestampTimeField(TimeField):
#     def process_formdata(self, valuelist):
#         if valuelist:
#             time_str = ' '.join(valuelist)
#             try:
#                 self.data = datetime.time(
#                     *time.strptime(time_str, self.format)[3:6]
#                 )
#             except ValueError:
#                 self.data = None
#                 raise ValueError(self.gettext(self.error_msg))


class SubscriptionForm(FlaskForm):
    url = HiddenField('数据地址', validators=[DataRequired()])
    #FIXME x@139com
    email = EmailField('接收邮箱', validators=[Email(), DataRequired()])
    time = TimeField('提醒时间', validators=[DataRequired])
    