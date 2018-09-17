from odoo import api, fields, models, _
from odoo.tools.translate import html_translate
# from oauthlib.oauth1.rfc5849.endpoints import access_token

class kaijin_waiver_otp(models.Model):

    _name = 'kaijin.waiver.otp'
    access_token = fields.Char(string='Access Token',default=None,required=True)
    otp = fields.Char(string='Url',default=None,required=True)
    email_to = fields.Char(string='E-mail id',default=None,required=True)   
