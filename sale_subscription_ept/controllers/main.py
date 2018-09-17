from odoo import http,_
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
import base64
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import UserError

class KaijinAgreement(http.Controller):
    
#    load a student profile form
    @http.route('/kaijin_billing_agreement', type='http',auth='public', website=True)
    def kaijin_billing_agreement(self,**kwargs):
        partner_id=request.website.sale_get_order().partner_id
        product=request.website.sale_get_order().order_line.filtered(lambda order: order.product_id.recurring_invoice == True).product_id
#         payer_name=request.env[]
        waiver_id=request.env['kaijin.waiver'].sudo().search([('partner_id','=',partner_id.id)])
        membership_type="Active"
        contract_type="Month to Month Subscription"
        payment_amount=request.website.sale_get_order().order_line.filtered(lambda order: order.product_id.recurring_invoice == True).product_id.list_price
        vals={
            'name':partner_id.name,
            'product':product.display_name,
            'payer_name':waiver_id.parent_name or waiver_id.name,
            'product_id':product.id,
            'membership_type':membership_type,
            'contract_type':contract_type,
            'monthly_payment':payment_amount
            }
        return request.render("sale_subscription_ept.kaijin_billing_agreement",vals)
    
    @http.route(['/my/signature/accept'], type='json', auth="public", website=True)
    def signature_accept(self, res_id, access_token=None, partner_name=None, signature=None,**post):
        if not signature:
            return {'error': _('Signature is missing.')}
        order_id=request.env['mail.message'].search([('res_id','=',res_id)])
        if order_id:
            order_id.sudo().unlink()
        _message_post_helper(
            res_model='sale.order',
            res_id=res_id,
            message=_('Order signed by %s') ,
            attachments=[('signature.png', base64.b64decode(signature))] if signature else [],
            **({'token': access_token} if access_token else {}))
        return {
            'success': _('Your signature has been confirmed.'),
            'redirect_url': '/shop/checkout',
        }
        
    @http.route('/kaijin_billing_agreement_submit', type='http',auth='public', website=True)
    def kaijin_billing_agreement_submit(self,**post):
        product_id=request.website.sale_get_order().order_line.filtered(lambda order: order.product_id.recurring_invoice == True).product_id
        partner_id=request.website.sale_get_order().partner_id
        kaijin_agreement_id=request.env['kaijin.agreement'].sudo().search([('partner_id','=',partner_id.id)])
        if kaijin_agreement_id:
            kaijin_agreement_id.sudo().unlink()
        res=request.env['kaijin.agreement'].sudo().create({
                 'partner_id':partner_id.id,
                 'product_id':product_id.id,
                 'payer_name':post.get('payer_name',None),
                 'contract_type':post.get('contract_type',None),
                 'monthly_payment':post.get('monthly_payment',None),
                 'bill_payment_date':post.get('bill_payment_date',None),
                 'service_start_date':post.get('service_start_date',None),
                 'service_expiration_date':post.get('service_expiration_date',None),
                 })
        return request.redirect('/shop/checkout')
    
class WebsiteSale(WebsiteSale):
    
    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        res = super(WebsiteSale, self).checkout( **post)
        is_service=request.website.is_service()
        if is_service:
            order = request.website.sale_get_order()
            order_id=order.id
            order_id=request.env['mail.message'].search([('res_id','=',order_id),('body','like','Order signed by')])
            agreement_id= request.env['kaijin.agreement'].sudo().search([('partner_id','=',request.env.user.partner_id.id)])
            if order_id and agreement_id:
                return res
            else:
                return request.redirect('/shop/cart')
        else:
            return res
                
    @http.route(['/check_for_service'], type='json', auth="public", website=True)
    def check_for_service(self, **post):
        return request.website.is_service()
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product=request.website.sale_get_order().order_line.filtered(lambda order: order.product_id.recurring_invoice == True).product_id
        products=request.env['product.product'].sudo().search([('id','=',product_id)]).recurring_invoice
        if products and request.website.is_public_user():
            return request.render('sale_subscription_ept.for_subscription_login')
        if products and product:
            return request.render('sale_subscription_ept.already_subscription')
        if products:
            #agreement_id= request.env['kaijin.agreement'].sudo().filtered(lambda order: order.partnert_id.id == request.website.sale_get_order().partner_id.id )
            agreement_ids= request.env['kaijin.agreement'].sudo().search([('partner_id','=',request.env.user.partner_id.id)])
            if  agreement_ids:
                if agreement_ids.has_subscription:
                    return request.render('sale_subscription_ept.already_subscription')
                else:
                    agreement_ids.sudo().unlink()
                    res = super(WebsiteSale, self).cart_update(product_id,add_qty=1, set_qty=0, **kw)
                    return res
            else:
                res = super(WebsiteSale, self).cart_update(product_id,add_qty=1, set_qty=0, **kw)
                return res
        else:
            res = super(WebsiteSale, self).cart_update(product_id,add_qty=1, set_qty=0, **kw)
            return res

