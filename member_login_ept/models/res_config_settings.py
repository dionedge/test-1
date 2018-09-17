from odoo import models, fields, api, exceptions, _



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    truancy_report_mail_template_id = fields.Many2one('mail.template',string="Mail Template")
    truancy_report_number_of_days = fields.Integer(string='Number Of Days')
    
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            truancy_report_mail_template_id=int(get_param('truancy_report_mail_template_id')) or False,
            truancy_report_number_of_days=int(get_param('truancy_report_number_of_days')) or False
        )
        return res
    
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('truancy_report_mail_template_id',self.truancy_report_mail_template_id.id)
        params.set_param('truancy_report_number_of_days',self.truancy_report_number_of_days)
