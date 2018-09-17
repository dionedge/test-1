from odoo import api, fields, models, _,SUPERUSER_ID
import string
import random
import uuid
import werkzeug.urls
from odoo.exceptions import UserError



class crm_lead(models.Model):
    
    _inherit = ["crm.lead"]
    
    access_token = fields.Char(string='Access Token',default=None)
    url = fields.Char(string='Url',default=None)
    is_access_token_active = fields.Boolean(default=True)
    is_link_active = fields.Boolean(default=True)
    kaijin_waiver_id = fields.Many2one('kaijin.waiver', string="Student Profile ")# record of student profile
    waiting = fields.Boolean(default=False)
    state_user = fields.Selection([('New', 'NEW'), ('Waiting','Waiting'),('Done','Done')], string='Status', required=True, readonly=True, copy=False, default='New')
    is_parent_name=fields.Boolean(string='Is Parent name required? ')
    starting_date = fields.Date(string='Start date')
    ending_date = fields.Date(string='End date')
    
#   Send e-mail with token generated link
    @api.multi
    def invitation_mail(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        random_token=str(uuid.uuid4())  
        if self.email_from and self.contact_name:
            try:
                self.sudo().write({
                    'access_token': random_token,
                    'waiting':True,
                    'is_access_token_active': True
                    })
                link='%s/student_profile/%s?db=%s'%(url,self.access_token,self._cr.dbname) 
                self.sudo().write({'url':link})
                template = self.env.ref('website_crm_ept.invitation_mail_template')
                template.sudo().send_mail(self.id, force_send=True, raise_exception=True)
                send_from=self.env['res.users'].sudo().search([('id','=',SUPERUSER_ID)])
                send_to=self.contact_name
                body='Mail is send to '+send_to+' by '+send_from.name           
                self.message_post(body)
                self.state_user="Waiting"    
                return True
            except :
                raise Warning(_('Some thing goes wrong'))
        else:
            raise UserError(_("Enter Fields e-mail and Contact Name "))
   
    
    
    
