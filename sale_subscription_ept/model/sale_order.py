
import logging
_logger = logging.getLogger(__name__)
import datetime
from odoo import fields, models,api, _
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"
    
    @api.multi
    def _action_confirm(self):
        # added by priyam
        # use close all send mail of sale order
        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
#         if self.env.context.get('send_email'):
#             self.force_quotation_send()

        # create an analytic account if at least an expense product
        if any([expense_policy != 'no' for expense_policy in self.order_line.mapped('product_id.expense_policy')]):
            if not self.analytic_account_id:
                self._create_analytic_account()
        return True

    def _prepare_subscription_data(self, template):
        """Prepare a dictionnary of values to create a subscription from a template."""
        values = super(SaleOrder, self)._prepare_subscription_data(template)
        agreement_id= self.env['kaijin.agreement'].sudo().search([('partner_id','=',self.partner_id.id)])
        if agreement_id:
            if not agreement_id.has_subscription:
                values['date_start']=agreement_id.service_start_date
                values['state']='draft'
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                invoicing_period = relativedelta(**{periods[template.recurring_rule_type]: template.recurring_interval})
                recurring_next_date = fields.Date.from_string(agreement_id.service_start_date) + invoicing_period
                values['recurring_next_date'] = fields.Date.to_string(recurring_next_date)
                
                #added by artip
                subscription_id=self.order_line.filtered(lambda order: order.product_id.recurring_invoice == True).product_id
                if subscription_id:
                  
                    agreement_id.sudo().write({'has_subscription':True})
                    self.partner_id.sudo().write({'billing_id':agreement_id.id})
        #added by artip over
        return values
    
   
    
    @api.multi
    def _prepare_invoice(self):
        # added by priyam    
        res = super(SaleOrder, self)._prepare_invoice()
        agreement_id = self.env['kaijin.agreement'].sudo().search([('partner_id','=',self.partner_id.id)],limit=1)
        if agreement_id and agreement_id.service_start_date and not agreement_id.sale_order_id :
            end_service_date =datetime.datetime.strptime(agreement_id.service_start_date, "%Y-%m-%d") + relativedelta(months=1)
            res.update({'start_service_date' : agreement_id.service_start_date,'end_service_date' : end_service_date})
            agreement_id.write({'sale_order_id' : self.id })
        return res
