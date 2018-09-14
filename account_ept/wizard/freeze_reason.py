
import datetime as dt
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning

class MembershipFreezeReason(models.TransientModel):
    _name= 'membership.freeze.reason.wizard'
    
    freeze_reason = fields.Text()
    accept_data = fields.Boolean(default=True)
    start_freeze_date = fields.Date("Starting Date :  ")
    stop_freeze_date = fields.Date("Ending Date :  ")
    
    @api.multi
    def send_message(self):
        invoice_id = self.env['account.invoice'].browse(self.env.context.get('default_res_id'))
        body = self.freeze_reason
        invoice_id.message_post(body)
        force_send = True
        template_obj = self.env.ref('account_ept.freeze_membership_template')
        partner_id = self.env['res.users'].browse(tools.SUPERUSER_ID)
        template_obj['email_to'] = partner_id.partner_id.email
        template_obj.send_mail(invoice_id.id,force_send)
        invoice_id.write({'state':'freeze','freeze_membership': False})
        return True
    
    @api.constrains('stop_freeze_date')
    def _check_end_date(self):
        if self.start_freeze_date and self.stop_freeze_date:
            converted_start_date = dt.datetime.strptime(self.start_freeze_date, "%Y-%m-%d")
            end_freeze_period = converted_start_date + dt.timedelta(days = 90)
            end_freeze_date= dt.datetime.strftime(end_freeze_period ,'%Y-%m-%d' )
            start_freeze_date = dt.datetime.strftime(converted_start_date,'%Y-%m-%d' )
            converted_stop_date = dt.datetime.strftime(dt.datetime.strptime(self.stop_freeze_dateto , "%Y-%m-%d"), "%Y-%m-%d")
            if self.stop_freeze_date >= end_freeze_date:
                raise Warning(_('You can not insert End date more than 3 months from start date !!'))
            if start_freeze_date  <= dt.datetime.strftime(fields.datetime.today(),'%Y-%m-%d'):
                raise Warning(_('You can not insert Start date less than today date !!'))
            if converted_stop_date <= dt.datetime.strftime(fields.datetime.today(),'%Y-%m-%d'):
                raise Warning(_('You can not insert End date less than today date !!'))
            
        
        