from odoo import fields, models,api, _

class website(models.Model):
    _inherit = 'website'
    
    @api.multi
    def is_service(self):
        subscription_product=self.sale_get_order().order_line.filtered(lambda order: order.product_id.recurring_invoice == True)
        if subscription_product:
            return True
        else:
            return False

