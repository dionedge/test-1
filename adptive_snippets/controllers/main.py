from odoo import http
from odoo.http import request

class LoadShop(http.Controller):
    
    @http.route('/load_shop', type='http',auth='public', website=True)
    def load_shop(self,token=None,db=None,**kwargs):
        return request.render('adptive_snippets.website_shop')
    
    @http.route(['/blog_data'],type='json', auth='public', website=True , csrf=False, cache=30)
    def category_data(self,template):
        data=request.env['blog.post'].search([('website_published','=',True)],order='post_date desc',limit=3)
        values = {'object':data}
        return request.env.ref(template).render(values)