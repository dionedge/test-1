from odoo import http
from odoo.http import request
from odoo import api, fields, models, _,SUPERUSER_ID
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale
import random
from odoo.exceptions import UserError
from urllib.parse import urljoin
import uuid
import json
from requests import get
import werkzeug
import base64

class student_profile(http.Controller):
    
#    load a student profile form
    @http.route('/student_profile/<string:token>', type='http',auth='public', website=True)
    def student_profile(self,token=None,db=None,**kwargs):
        ensure_db()
        record=request.env['crm.lead'].sudo().search([('access_token','=',token)])
        if record and record.__len__() ==1:
            if record.is_access_token_active and record.is_link_active:
                record.sudo().write({'is_link_active':False})
                values={
                'name':record.contact_name,
                'email':record.email_from,
                'token':record.access_token,
                'phone':record.phone,
                
                }
                return request.render("website_crm_ept.student_profile_form",values)
            else:
                values={
                'is_success':True
                }
                return request.render("website_crm_ept.contactus_thanks_template",values)
        else:
                values={
                'is_success':False
                }
                return request.render("website_crm_ept.contactus_thanks_template",values)
    
#    Write a record of student profile
    @http.route('/student_profile_submit', type='http', auth='public', website=True)
    def student_profile_submit(self, **post):
        record=request.env['crm.lead'].sudo().search([('access_token','=',post['token'])])
        record.sudo().write({'street':post.get('address',None),})
        if record:
            if record.is_access_token_active:
                res=request.env['kaijin.waiver'].sudo().create({
                'name':post.get('student_name',None),
                'date_of_birth':post.get('dob',None),
                'parent_name':post.get('parent_name',None),
                'address':post.get('address',None),
                'email':post.get('email',None),
                'phone':post.get('mobile',None),
                'emergency_contact':post.get('emergency_phone',None),
                'health':post.get('health_condition',None),
                'experience':post.get('previous_experience',None),
                'starting_date':post.get('starting_date',None),
                'ending_date':post.get('ending_date',None)
                })
                record.sudo().write({ 
                    'is_access_token_active': False,
                    'waiting':False,
                    'state_user':'Done',
                    'kaijin_waiver_id' : res.id,
                    'starting_date':post.get('starting_date',None),
                    'ending_date':post.get('ending_date',None)
                    })
                val={'name':'convert','user_id':request.env['res.users'].sudo().search([('id','=',SUPERUSER_ID)]).id,'team_id':record.team_id.id,'action':'create'}
                opportunity_id= request.env['crm.lead2opportunity.partner'].sudo().create(val)
                val={'lead_ids':record.id,'team_id':record.team_id.id,'user_id':request.env['res.users'].sudo().search([('id','=',SUPERUSER_ID)]).id}
                opportunity=opportunity_id._convert_opportunity(val)
                res.sudo().write({'partner_id':record.partner_id.id})
                author_id = request.env['res.users'].sudo().search([('id','=',SUPERUSER_ID)]).id
                query = {'db': request._cr.dbname}
                grp=request.env['res.groups'].sudo().search([]).filtered(lambda r : r.get_xml_id().popitem()[1] in 'sales_team.group_sale_manager')
                recipient_partners = []
                fragment = {
                         'id': record.id,
                         'model': 'crm.lead',
                         }
                recipient_partners.append(record.user_id.partner_id.id)
                base_url_ept = request.env['ir.config_parameter'].sudo().get_param('web.base.url')        
                url = urljoin(base_url_ept, "web?%s#%s" % (werkzeug.url_encode(query), werkzeug.url_encode(fragment)))
                body='<a href='+url+'>'+record.name+'</a><br/>Name :'+record.contact_name+'<br/>Email :'+record.email_from+'<br/>Phone :'+record.phone
                if record.user_id.partner_id.id:
                    request.env['mail.message'].sudo().create({'author_id' : author_id,'message_type' : 'comment','partner_ids' : [(6, 0,recipient_partners)],'record_name':"lead message",'subject' : "Opportunity  is created",'body' : body})
                if post['parent_name']=='':
                    record.sudo().write({'is_parent_name':False })
                else:
                    record.sudo().write({'is_parent_name':True})

                return request.redirect("/contactus-thank-you")
            else:
                values={
                'reg_message ':"You have already Registered."
                }
                return request.render("website_crm_ept.contactus_thanks_template",values)
        else:
                values={
                'reg_message ':"There Is same issue"
                }
                return request.render("website_crm_ept.contactus_thanks_template",values)
       
class WebsiteForm(WebsiteForm):
     
    def insert_record(self, request, model, values, custom, meta=None):
        # add by priyam
        res = super(WebsiteForm, self).insert_record(request, model, values, custom, meta)
        lead = request.env['crm.lead'].sudo().search([('id','=',res)])
        if 'description' in values and values.get('description') :
            lead.write({'description' :"Question : %s" %(values.get('description'))})
        return res
    
        
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        
        res = super(WebsiteForm, self).website_form(model_name, **kwargs)         # edit by priyam
        if request.params.get('student_form',False):
            #country=request.env['res.country'].sudo().search([('code','in',request.params.get('country'))])
            
            mail_id=request.params.get('email_from',False)
            otp_key=request.params.get('otp_key',False)
            otp=request.params.get('otp',False)
            country_id=request.env['res.country'].sudo().search([('code','=',request.params.get('country'))]).id
            state_id=request.env['res.country.state'].sudo().search([('name','=',request.params.get('state'))]).id
            zip=request.params.get('zip',False)
            city=request.params.get('city',False)
            otp_id=request.env['kaijin.waiver.otp'].sudo().search([('email_to','=',mail_id),('access_token','=',otp_key),('otp','=',otp)])
            if otp_id:
                del request.params['student_form']  
                del request.params['g-recaptcha-response']
                del request.params['otp_key']
                del request.params['otp']
             
                otp_id.sudo().unlink()
                
                response_data = json.loads(res.get_data(as_text=True))
                if 'id' in response_data:  # a new lead has been created
                    lead_model = request.env['crm.lead']
                    lead = lead_model.sudo().search([('id','=',(response_data['id']))])
                    lead.sudo().write({'country_id': country_id or False,
                                       'state_id':state_id or False,
                                       'city':city or False,
                                       'zip':zip or False,
                        })
                
                author_id = request.env['res.users'].sudo().search([('id','=',SUPERUSER_ID)]).id
                query = {'db': request._cr.dbname}
                grp=request.env['res.groups'].sudo().search([]).filtered(lambda r : r.get_xml_id().popitem()[1] in 'sales_team.group_sale_manager')
                recipient_partners = []
                fragment = {
                         'id': lead.id,
                         'model': 'crm.lead',
                         }
                for recipient in grp.users: 
                    recipient_partners.append(recipient.partner_id.id)
                base_url_ept = request.env['ir.config_parameter'].sudo().get_param('web.base.url')  
                url = urljoin(base_url_ept, "web?%s#%s" % (werkzeug.url_encode(query), werkzeug.url_encode(fragment)))
                body='<a href='+url+'>'+request.params['name']+'</a><br/>Name :'+request.params['contact_name']+'<br/>E-mail :'+request.params['email_from']+'<br/>Phone :'+request.params['phone']
                request.env['mail.message'].sudo().create({'author_id' : author_id,'message_type' : 'comment','partner_ids' : [(6, 0,recipient_partners)],'record_name':"lead message",'subject' : "New lead is created",'body' : body})
                return res
            else:
                return json.dumps(False)
        # edit by priyam
        else :
            return res
    
    @http.route('/send_otp', type='json', auth="public", methods=['POST'], website=True)
    def send_otp(self, mail_id,name, **kwargs):
        RandomNumber = ''.join(random.choice('0123456789') for _ in range(6))
        random_token=str(uuid.uuid4())
        request_ip = request.httprequest.environ.get("HTTP_X_REAL_IP", False)

        
        if (mail_id and name):
            try:
                res=request.env['kaijin.waiver.otp'].sudo().create({
                    'access_token':random_token,
                    'otp':RandomNumber,
                    'email_to':mail_id,
                })
                template = request.env.ref('website_crm_ept.otp_mail_template')
                template.sudo().send_mail(res.id, force_send=True, raise_exception=True)
                return random_token
            except :
                raise Warning(_('Some thing goes wrong'))
        else:
            raise UserError(_("Enter Fields e-mail and Contact Name "))    
        
    @http.route('/send_otp_timeout', type='json', auth="public", methods=['POST'], website=True)
    def send_otp_timeout(self, mail_id,otp_key, **kwargs):
        res=request.env['kaijin.waiver.otp'].sudo().search([('email_to','=',mail_id),('access_token','=',otp_key)])
        res.sudo().unlink()
        return True

    @http.route('/send_otp_check', type='json', auth="public", methods=['POST'], website=True)
    def send_otp_check(self, mail_id,otp_key,otp,**kwargs):
        res=request.env['kaijin.waiver.otp'].sudo().search([('email_to','=',mail_id),('access_token','=',otp_key),('otp','=',otp)])
        if res:
            return True
        else:
            return False
        
    
        
    

    
    
