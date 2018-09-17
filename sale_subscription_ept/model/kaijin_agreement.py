from odoo import api, fields, models, _
import datetime

class kaijin_agreement(models.Model):
    
    _name = 'kaijin.agreement'
    _rec_name = 'partner_id'
    
    
    partner_id = fields.Many2one('res.partner', string="Client Profile")
    product_id = fields.Many2one('product.product', string="Subscription Product")
    membership_type=fields.Boolean(default=True)
    payer_name = fields.Char(string='Payer Name')
    contract_type = fields.Char(string='Contract Type')
    monthly_payment = fields.Char(string='Monthly Payment Amount')
    bill_payment_date = fields.Date(string='Bill Payment Date')
    service_start_date = fields.Date(string='Service Start Date')
    service_expiration_date = fields.Date(string='Service Expiration  Date')
    has_subscription=fields.Boolean(default=False)
    
    #added by priyam     
    sale_order_id = fields.Many2one('sale.order', string = "Sale Order")
    
    @api.model
    def start_subscription(self):
        # added by priyam         
        today = datetime.date.today()
        today = fields.Date.to_string(today)
        agreement_ids = self.env['kaijin.agreement'].search([('service_start_date', '=',today)])
        for agreement_id in agreement_ids:
            subscription_id=self.env['sale.subscription'].sudo().search([('partner_id','=',agreement_id.partner_id.id)])
            subscription_id.write({'state' : 'open'})  
