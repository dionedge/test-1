
import datetime
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    '''use for send mail to saleperson of opportunity end_date after 3 days for contact manually'''
    def _opportunity_enddate_remainder(self):
        # added by priyam 
               
        current_date=datetime.datetime.now()
        date_3days_ago = (current_date-datetime.timedelta(days=3)).strftime('%Y-%m-%d')
        template = self.env.ref('crm_ept.opportunity_remainder_id')
        stage = self.env.ref('crm_ept.stage_lead5')
        opportunity_ids = self.env['crm.lead'].sudo().search([('type','=','opportunity'),('stage_id','=',stage.id)])
        for opportunity_id in opportunity_ids :
            if opportunity_id.ending_date :
                end_date = opportunity_id.ending_date.split(' ')[0] 
                if end_date == date_3days_ago and template :
                    template.sudo().send_mail(opportunity_id.id,force_send=True)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification', subtype=None, parent_id=False, attachments=None, content_subtype='html', **kwargs):
        # auto pin 'direct_message' channel partner
#         self.filtered(lambda res_config_settings: res_config_settings.channel_type == 'chat').mapped('template_id')
        ctx = dict(self._context) or {}
        if self._name == 'crm.lead' and subtype == 'mail.mt_comment':
            ctx.update({'mail_save_message_last_post':True})
        message = super(CrmLead, self.with_context(ctx)).message_post(body=body, subject=subject, message_type=message_type, subtype=subtype, parent_id=parent_id, attachments=attachments, content_subtype=content_subtype, **kwargs)
        return message
    
#     Added by KM
    
    @api.model
    def send_customer_portal_access_mail(self):
        opportunities = self.env['crm.lead'].search([('type', '=', 'opportunity'),('stage_id','=',1)])
        for oppo in opportunities:
            if oppo.starting_date and oppo.starting_date >= fields.Date.today(): 
                if oppo.partner_id:
                    if oppo.email_from:
                        PortalWizard_obj = self.env['portal.wizard']
                        record = PortalWizard_obj.with_context(active_ids=oppo.partner_id.ids).create({
                            'portal_id' : self.env['res.groups'].search([('id','=',9)]).id
                            })
                        record.onchange_portal_id()
                        if record.user_ids[0].in_portal == False:
                            record.user_ids[0].in_portal = True
                        record.action_apply()
                        oppo.write({'stage_id':5})
                        body = "Mail containing details of Portal access is sent to customer" + oppo.partner_id.name + "Trial Period is started !!"
                        oppo.message_post(body)
            else:
                return True
                
    @api.model
    def check_waiver_form(self):
        all_leads = self.env['crm.lead'].search([])
        for single_id in all_leads:
            if single_id.kaijin_waiver_id or single_id.state_user == 'Waiting':
                continue
            else:
                single_id.invitation_mail()
                
    @api.model
    def trial_expired(self):
        inactive_opportunities = self.env['crm.lead'].search([('type', '=', 'opportunity'),('stage_id','=',5)])
        for op in inactive_opportunities:
            if op.starting_date and op.ending_date:
                if  op.ending_date == datetime.datetime.today().strftime('%Y-%m-%d'):
                    template = self.env.ref('crm_ept.trial_expiration_mail')
                    template.send_mail(op.id, force_send=True, raise_exception=True)
                    body = "Trial period expiration mail sent to customer" + op.partner_id.name
                    op.message_post(body)
                
                # KM Over            
