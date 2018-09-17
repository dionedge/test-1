from odoo import fields, models,api, _
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):

    _inherit = "res.partner"
    
    billing_id = fields.Many2one('kaijin.agreement', string="Agreement")