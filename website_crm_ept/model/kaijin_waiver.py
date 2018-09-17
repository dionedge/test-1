from odoo import api, fields, models, _


class kaijin_waiver(models.Model):
    
    _name = 'kaijin.waiver'
    
    name = fields.Char(string='Student Name')
    date_of_birth = fields.Date(string='Date of Birth')
    parent_name = fields.Char(string='Parent Name')
    address = fields.Char(string='Address')
    email = fields.Char(string='E-mail')
    phone = fields.Char(string='Phone')
    emergency_contact=fields.Char(string='Emergency Contact')
    health = fields.Char(string='Health Conditions / Injuries')
    experience =fields.Char(string='Previous Experience')
    starting_date = fields.Date(string='Start date')
    ending_date = fields.Date(string='End date')
    partner_id =fields.Many2one('res.partner', string="Student")
