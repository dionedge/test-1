from odoo import fields, models,api, _
    
class website(models.Model):
    
    _inherit = 'website'
    
    @api.multi
    def is_service(self):
        flag=None
        oreder_line=self.sale_get_order().order_line
        for order in oreder_line:
            if order.product_id.product_tmpl_id.type=='service':
                flag=True
        if flag:
            return True
        else:
            return False
