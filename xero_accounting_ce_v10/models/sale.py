from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def add_suffix_ysi_vendors(self):
        vend_obj = self.env['product.supplierinfo'].search([])
        for vo in vend_obj:
            if vo.name.name == 'YSI' and vo.product_code and vo.product_code[-4:] != '_YSI':
                vo.product_code = vo.product_code + '_YSI'
        prod_obj = self.env['product.product'].search([])
        for po in prod_obj:
            for vend in po.seller_ids:
                if vend.name.name == 'YSI' and po.default_code[-4:] != '_YSI':
                    po.default_code = po.default_code + '_YSI'
