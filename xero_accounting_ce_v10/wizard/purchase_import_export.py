import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class purchase_import_export(models.TransientModel):
    _name = 'purchase.import.export'
    _description = 'Import Export Purchase Order'

    purchase_order_ids = fields.Many2many('purchase.order', 'export_purchase_rel', 'wizard_id', 'po_id', 'Purchase Orders')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.multi
    def export_purchase_order(self):
        """ Export Purchase Order's from OpenERP to Xero"""
        company = self.env.user.company_id
        _logger.info("...Exporting Purchase Order's...")
        if self.purchase_order_ids:
            purchase_orders = [po for po in self.purchase_order_ids if po.company_id.id == company.id]
            if purchase_orders:
                purchase_orders[0].export_purchase_order(purchase_orders)
        self._cr.commit()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def case_close(self):
        return {'type': 'ir.actions.act_window_close'}
