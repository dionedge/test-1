
import datetime
from odoo import api, models, _, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
            ('freeze', 'Membership Freezed')
        ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used when the invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice."
             " * The 'Membership Freezed is set autmatically when user freeze his membership.'")

    # added by priyam     
    freeze_membership = fields.Boolean(string = 'Freeze Membership')
    start_service_date = fields.Date(string = "Start Service")
    end_service_date = fields.Date(string = "Renew service")
    
    
    @api.multi
    def action_invoice_paid(self):
        if self.id:
            self.ensure_one()
            res = self.action_invoice_sent()
            super(AccountInvoice, self).action_invoice_paid()
            self.write({'action_invoice':True})
            return res
    
    @api.multi
    def action_freeze_reason(self):
        ctx = dict(
                default_res_id=self.id,
                )
        return {
            'name': _('Freeze Membership'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'membership.freeze.reason.wizard',
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
    
    @api.multi
    def action_invoice_open(self):
        service_type = False
        res = super(AccountInvoice, self).action_invoice_open()
        if self.invoice_line_ids:
            for l in self.invoice_line_ids:
                if l.product_id and l.product_id.type:
                    if l.product_id.type == 'service':
                        service_type = True
        if self.date_invoice and service_type  == True:
            converted_start_date = datetime.datetime.strptime(self.date_invoice, "%Y-%m-%d")
            renew_subs_period = converted_start_date + datetime.timedelta(days = 30)
            self.subs_renew_date= datetime.datetime.strftime(renew_subs_period ,'%Y-%m-%d' )
        return res
        
    @api.model
    def freeze_membership_button_visiblity(self):
        # added by priyam
        invoices = self.env['account.invoice'].search([('state','=','paid')])
        for invoice in invoices :
            all_partner_invoice = self.env['account.invoice'].search([('state','=','paid'),('partner_id','=',invoice.partner_id.id),('start_service_date','<=',datetime.date.today().strftime('%Y-%m-%d')),('end_service_date','>',datetime.date.today().strftime('%Y-%m-%d')),('invoice_line_ids.product_id.type','=','service')])
            if len(all_partner_invoice) == 1 :
                all_partner_invoice.write({'freeze_membership' : True})    
        