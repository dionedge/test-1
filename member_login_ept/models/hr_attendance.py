
from odoo import models, fields

class ClassesEpt(models.Model):
    _inherit = "hr.attendance"
    
    class_id = fields.Many2one('classes.ept',"Class")
    
    
