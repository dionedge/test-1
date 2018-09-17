from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
from dateutil.relativedelta import relativedelta
import datetime
import time
import traceback
        
class sale_subcription(models.Model):
    _inherit = 'sale.subscription'

    @api.multi
    def _recurring_create_invoice(self, automatic=False):
        # added by priyam
        # use close all send mail of subscription and create invoice when active member is True 
        auto_commit = self.env.context.get('auto_commit', True)
        cr = self.env.cr
        invoices = self.env['account.invoice']
        current_date = time.strftime('%Y-%m-%d')
        imd_res = self.env['ir.model.data']
        template_res = self.env['mail.template']
        if len(self) > 0:
            subscriptions = self
        else:
            domain = [('recurring_next_date', '<=', current_date),
                      ('state', 'in', ['open', 'pending'])]
            subscriptions = self.search(domain)
        if subscriptions:
            sub_data = subscriptions.read(fields=['id', 'company_id'])
            for company_id in set(data['company_id'][0] for data in sub_data):
                sub_ids = [s['id'] for s in sub_data if s['company_id'][0] == company_id]
                subs = self.with_context(company_id=company_id, force_company=company_id).browse(sub_ids)
                context_company = dict(self.env.context, company_id=company_id, force_company=company_id)
                for subscription in subs:
                    if automatic and auto_commit:
                        cr.commit()
                    # payment + invoice (only by cron)
                    if subscription.template_id.payment_mandatory and subscription.recurring_total and automatic:
                        try:
                            payment_token = subscription.payment_token_id
                            if payment_token and subscriptions.partner_id.active_member:
                                invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                                new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
                                new_invoice.message_post_with_view('mail.message_origin_link',
                                    values = {'self': new_invoice, 'origin': subscription},
                                    subtype_id = self.env.ref('mail.mt_note').id)
                                new_invoice.with_context(context_company).compute_taxes()
                                tx = subscription._do_payment(payment_token, new_invoice, two_steps_sec=False)[0]
                                # commit change as soon as we try the payment so we have a trace somewhere
                                if auto_commit:
                                    cr.commit()
                                if tx.state in ['done', 'authorized']:
                                    subscription.send_success_mail(tx, new_invoice)
                                    msg_body = 'Automatic payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.invoice data-oe-id=%d>View Invoice</a>.' % (tx.id, tx.reference, tx.amount, new_invoice.id)
                                    subscription.message_post(body=msg_body)
                                    if auto_commit:
                                        cr.commit()
                                else:
                                    _logger.error('Fail to create recurring invoice for subscription %s', subscription.code)
                                    if auto_commit:
                                        cr.rollback()
                                    new_invoice.unlink()
                            amount = subscription.recurring_total
                            date_close = datetime.datetime.strptime(subscription.recurring_next_date, "%Y-%m-%d") + relativedelta(days=15)
                            close_subscription = current_date >= date_close.strftime('%Y-%m-%d')
                            email_context = self.env.context.copy()
                            email_context.update({
                                'payment_token': subscription.payment_token_id and subscription.payment_token_id.name,
                                'renewed': False,
                                'total_amount': amount,
                                'email_to': subscription.partner_id.email,
                                'code': subscription.code,
                                'currency': subscription.pricelist_id.currency_id.name,
                                'date_end': subscription.date,
                                'date_close': date_close.date()
                            })
                            if close_subscription:
                                _, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_close')
#                                 template = template_res.browse(template_id)
#                                 template.with_context(email_context).send_mail(subscription.id)
                                _logger.debug("Sending Subscription Closure Mail to %s for subscription %s and closing subscription", subscription.partner_id.email, subscription.id)
                                msg_body = 'Automatic payment failed after multiple attempts. Subscription closed automatically.'
                                subscription.message_post(body=msg_body)
                            else:
                                _, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_reminder')
                                msg_body = 'Automatic payment failed. Subscription set to "To Renew".'
                                if (datetime.datetime.today() - datetime.datetime.strptime(subscription.recurring_next_date, '%Y-%m-%d')).days in [0, 3, 7, 14]:
#                                     template = template_res.browse(template_id)
#                                     template.with_context(email_context).send_mail(subscription.id)
                                    _logger.debug("Sending Payment Failure Mail to %s for subscription %s and setting subscription to pending", subscription.partner_id.email, subscription.id)
                                    msg_body += ' E-mail sent to customer.'
                                subscription.message_post(body=msg_body)
                            subscription.write({'state': 'close' if close_subscription else 'pending'})
                            if auto_commit:
                                cr.commit()
                        except Exception:
                            if auto_commit:
                                cr.rollback()
                            # we assume that the payment is run only once a day
                            last_tx = self.env['payment.transaction'].search([('reference', 'like', 'SUBSCRIPTION-%s-%s' % (subscription.id, datetime.date.today().strftime('%y%m%d')))], limit=1)
                            error_message = "Error during renewal of subscription %s (%s)" % (subscription.code, 'Payment recorded: %s' % last_tx.reference if last_tx and last_tx.state == 'done' else 'No payment recorded.')
                            traceback_message = traceback.format_exc()
                            _logger.error(error_message)
                            _logger.error(traceback_message)

                    # invoice only
                    else:
                        if subscriptions.partner_id.active_member :
                            try:
                                invoice_values = subscription.with_context(lang=subscription.partner_id.lang)._prepare_invoice()
                                new_invoice = self.env['account.invoice'].with_context(context_company).create(invoice_values)
                                new_invoice.message_post_with_view('mail.message_origin_link',
                                    values = {'self': new_invoice, 'origin': subscription},
                                    subtype_id = self.env.ref('mail.mt_note').id)
                                new_invoice.with_context(context_company).compute_taxes()
                                invoices += new_invoice
                                next_date = datetime.datetime.strptime(subscription.recurring_next_date or current_date, "%Y-%m-%d")
                                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                                invoicing_period = relativedelta(**{periods[subscription.recurring_rule_type]: subscription.recurring_interval})
                                new_date = next_date + invoicing_period
                                subscription.write({'recurring_next_date': new_date.strftime('%Y-%m-%d')})
                                if automatic and auto_commit:
                                    cr.commit()
                            except Exception:
                                if automatic and auto_commit:
                                    cr.rollback()
                                    _logger.exception('Fail to create recurring invoice for subscription %s', subscription.code)
                                else:
                                    raise
        return invoices

    def send_success_mail(self, tx, invoice):
        # added by priyam
        # use close all send mail of subscription
        imd_res = self.env['ir.model.data']
        template_res = self.env['mail.template']
        current_date = time.strftime('%Y-%m-%d')
        next_date = datetime.datetime.strptime(self.recurring_next_date or current_date, "%Y-%m-%d")
        periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
        invoicing_period = relativedelta(**{periods[self.recurring_rule_type]: self.recurring_interval})
        new_date = next_date + invoicing_period
        _, template_id = imd_res.get_object_reference('sale_subscription', 'email_payment_success')
        email_context = self.env.context.copy()
        email_context.update({
            'payment_token': self.payment_token_id.name,
            'renewed': True,
            'total_amount': tx.amount,
            'next_date': new_date.date(),
            'previous_date': self.recurring_next_date,
            'email_to': self.partner_id.email,
            'code': self.code,
            'currency': self.pricelist_id.currency_id.name,
            'date_end': self.date,
        })
        _logger.debug("Sending Payment Confirmation Mail to %s for subscription %s", self.partner_id.email, self.id)
#         template = template_res.browse(template_id)
#         return template.with_context(email_context).send_mail(invoice.id)


    def _prepare_invoice(self):
        # added by priyam         
        res = super(sale_subcription, self)._prepare_invoice()
        subscription = self.env['sale.subscription'].sudo().search([('partner_id','=',self.partner_id.id)],limit = 1)
        if subscription :
            end_service_date =datetime.datetime.strptime(subscription.recurring_next_date, "%Y-%m-%d") + relativedelta(months=1)
            res.update({'start_service_date' : subscription.recurring_next_date,'end_service_date' : end_service_date})
        return res
