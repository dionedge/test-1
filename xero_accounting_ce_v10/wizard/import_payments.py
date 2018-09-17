#  -*- encoding: utf-8 -*-
from datetime import datetime

from dateutil.parser import parse
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools.translate import _


class account_payment(models.Model):
    _inherit = 'account.payment'

    xero_paymentUp_date = fields.Datetime('Xero Update Date', readonly=True)
    xero_payment_code = fields.Char('Xero Payment Code')


class wiz_import_payments(models.TransientModel):
    """ Wizard for importing payments Xero to odoo from last updated date"""

    _name = 'wiz.import.payments'
    _description = 'Import Payments Wizard'

    @api.multi
    def import_payments(self):
        """ Import payments from Xero to OpenERP"""
        invoice_obj = self.env['account.invoice']
        payment_obj = self.env['account.payment']
        journal_obj = self.env['account.journal']
        currency_obj = self.env['res.currency']

        company = self.env['res.users'].browse(self._uid).company_id
        xero_client = company.get_xero_connection()

        invoice_ids = invoice_obj.search([('xero_exported', '=', True), ('state', 'in', ['open']), ('company_id', '=', company.id)])
        invoices_to_import = []
        opayment_ids = []
        payments = []
        if invoice_ids:
            for inv in invoice_ids:
                if inv.xero_invoice_id:
                    invoices_to_import.append(inv.xero_invoice_id)
        payment_xero_ids = payment_obj.search([('xero_paymentUp_date', '!=', None)])

        if invoices_to_import:
            if not payment_xero_ids:
                xero_response = xero_client.payments.all()

            if payment_xero_ids:
                max_date_list = max([pay_id.xero_paymentUp_date for pay_id in payment_xero_ids])
                n_date = parse(max_date_list)
                xero_response = xero_client.payments.filter(
                    since=datetime(n_date.year, n_date.month, n_date.day, n_date.hour, n_date.minute, n_date.second, n_date.microsecond))

            payments = xero_response or False
        if not payments:
            raise Warning('All Payments Already imported !')

        payments = isinstance(payments, list) and payments or [payments]
        import_payments = []
        for payment in payments:
            if payment['Invoice'].get('InvoiceID') and payment['Invoice']['InvoiceID'] in invoices_to_import and payment['Status'] == 'AUTHORISED':
                import_payments.append(payment)

        payments = import_payments
        if not payments:
            raise Warning('All Payments Already imported !')

        # Creating Vouchers for each payment
        count = 0
        for payment in payments:
            invoices = invoice_obj.search([('xero_invoice_id', '=', payment['Invoice']['InvoiceID'])])
            invoice = invoices and invoices[0]

            pay_type = None
            if payment['PaymentType'] == 'ACCRECPAYMENT':
                pay_type = 'sale'
            elif payment['PaymentType'] == 'ACCPAYPAYMENT':
                pay_type = 'purchase'

            journal_id = journal_obj.search([('default_debit_account_id.code', '=', str(payment['Account']['Code']))])

            if not journal_id:
                self.env['xero.logs'].create({
                    'name': 'Journal Not Defined for account : %s' % (payment['Account']['Code']),
                    'is_payment': True,
                    'state': 'error',
                    'invoice_id': invoice.id,
                    'date': datetime.now()
                })
                self._cr.commit()
                raise Warning('Journal Not Defined for account : %s' % (payment['Account']['Code']))

            payment_type = 'inbound' if pay_type == 'sale' else 'outbound'
            partner_id = invoice.partner_id.parent_id and invoice.partner_id.parent_id.id or invoice.partner_id.id
            journal = journal_id[0]
            payment_method = False
            if payment_type == 'inbound':
                payment_method = self.env.ref('account.account_payment_method_manual_in')
                journal_payment_methods = journal.inbound_payment_method_ids
            else:
                payment_method = self.env.ref('account.account_payment_method_manual_out')
                journal_payment_methods = journal.outbound_payment_method_ids
            if payment_method not in journal_payment_methods:
                self.env['xero.logs'].create({
                    'name': 'No appropriate payment method enabled on journal : %s' % (journal.name),
                    'is_payment': True,
                    'state': 'error',
                    'invoice_id': invoice.id,
                    'date': datetime.now()
                })
                self._cr.commit()
                raise Warning(_('No appropriate payment method enabled on journal %s') % journal.name)
            if payment['Invoice']:
                currency_id = currency_obj.search([('name', '=', payment['Invoice']['CurrencyCode'])])
                opayment_vals = {
                    'partner_id': partner_id,
                    'partner_type': ['supplier' if payment['Invoice']['Type'] == 'ACCPAY' else 'customer'][0],
                    'amount': float(payment['Amount']),
                    'currency_id': currency_id.id,
                    'journal_id': journal.id,
                    'payment_type': payment_type,
                    'payment_method_id': payment_method.id,
                    'invoice_ids': [(4, invoice.id, None)],
                    'xero_payment_code': payment['PaymentID'],
                    'xero_paymentUp_date': fields.datetime.now()
                }
            opayment_id = payment_obj.create(opayment_vals)
            opayment_ids.append(opayment_id)
            count = count + 1
        self.env['xero.logs'].create({
            'name': 'Payment Imported Successfully to Odoo',
            'state': 'success',
            'import_count': count,
            'is_payment': True,
            'date': datetime.now()})

        #  Confirming Payments
        if opayment_ids:
            for opayment_id in opayment_ids:
                opayment_id.post()
        self._cr.commit()
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def case_close(self):
        return {'type': 'ir.actions.act_window_close'}
