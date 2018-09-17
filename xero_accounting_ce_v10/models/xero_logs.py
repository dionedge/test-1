from odoo import models, fields


class xero_logs(models.Model):
    """ Keep track of Errors occurred when exporting Invoices"""
    _name = 'xero.logs'
    _description = 'Xero Logs'
    _order = 'date DESC'

    name = fields.Char('Description :', size=256)
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    purchaseorder_id = fields.Many2one('purchase.order', 'Purchase Order')
    product_id = fields.Many2one('product.product', 'Product')
    partner_id = fields.Many2one('res.partner', 'Customer')
    import_count = fields.Integer('No of Payments Imported :')
    export_count = fields.Integer('No of Invoice/Purchase Order Exported :')
    active = fields.Boolean('Active', default=True)
    is_payment = fields.Boolean('Payment', default=False)
    date = fields.Datetime('Date')
    state = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ])


xero_logs()
