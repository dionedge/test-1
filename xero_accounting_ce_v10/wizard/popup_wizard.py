import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class validate_wizard(models.TransientModel):
    _name = 'validate.wizard'
    _description = 'Validate Dialog Box'

    message = fields.Char("Message",
                          default=lambda self: ','.join([partner.encode('ascii', 'ignore') for partner in list(set(self._context['partner_name']))]))

    @api.multi
    def confirm_contact(self):
        if self._context.has_key('invoice_ids') and self._context['invoice_ids']:
            account_invoice_obj = self.env['account.invoice'].browse(self._context['invoice_ids'])
            self.env['invoice.wizard'].export_invoices(account_invoice_obj)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def cancel_contact(self):
        return {'type': 'ir.actions.act_window_close'}
