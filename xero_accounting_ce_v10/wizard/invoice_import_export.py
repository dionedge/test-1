import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class invoice_wizard(models.TransientModel):
    _name = 'invoice.wizard'

    invoice_ids = fields.Many2many('account.invoice', 'wizard_invoice_rel', 'invoice_wizard_id', 'origin_id', 'Invoices', )
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

    @api.model
    def default_get(self, fields):
        res = super(invoice_wizard, self).default_get(fields)
        context = dict(self._context or {})
        if context['active_model'] == 'account.invoice' and context['active_ids']:
            res['invoice_ids'] = context['active_ids']
        return res

    @api.multi
    def validate_wizard(self):
        '''Validating Invoice and Contact'''
        company = self.env.user.company_id
        if self.invoice_ids:
            invoices = [inv for inv in self.invoice_ids if inv.company_id.id == company.id]
            partner_list = []
            partner_name = []
            if invoices:
                for invoice in invoices:
                    is_partner_ref = invoice.partner_id.parent_id and invoice.partner_id.parent_id.ref or invoice.partner_id.ref
                    partner_list.append(is_partner_ref)
                    if not is_partner_ref:
                        partner_name.append(invoice.partner_id.parent_id and invoice.partner_id.parent_id.name or invoice.partner_id.name)
            invoice_ids_context = {'invoice_ids': [inv_id.id for inv_id in invoices], 'partner_name': partner_name}
            if False in partner_list:
                mod_obj = self.env['ir.model.data']
                res = mod_obj.get_object_reference('prag_xero_accounting_11', 'popup_partner_dialog_view')
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'New Contact Found In Odoo',
                    'res_model': 'validate.wizard',
                    'view_mode': 'form',
                    'view_id': [res and res[1] or False],
                    'context': invoice_ids_context,
                    'nodestroy': True,
                    'view_type': 'form',
                    'model': 'ir.ui.view',
                    'target': 'new',
                }
            else:
                res = self.export_invoices(self.invoice_ids)
                if res:
                    return {
                        'name': 'success msg reply',
                        'type': 'ir.actions.act_window',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'model': 'ir.ui.view',
                        'res_model': 'export.success.msg',
                        'target': 'new',
                    }
        self._cr.commit()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def export_invoices(self, invoice_ids):
        """  Exporting selected invoices to Xero Account """
        company = self.env.user.company_id
        _logger.info('...Exporting Invoices...')
        if invoice_ids:
            invoices = [inv for inv in invoice_ids if inv.company_id.id == company.id]
            if invoices:
                invoices[0].export_invoices(invoices)
        self._cr.commit()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def case_close(self):
        return {'type': 'ir.actions.act_window_close'}
