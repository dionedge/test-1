
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    template_id = fields.Many2one('mail.template',string="Mail Template")
    number_of_days = fields.Integer(string='Number Of Days')
    
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            template_id=int(get_param('template_id')) or False,
            number_of_days=int(get_param('number_of_days')) or False
        )
        return res
    
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        template_id = self.template_id.id
        number_of_days= self.number_of_days
        params.set_param('template_id',template_id)
        params.set_param('number_of_days',number_of_days)
