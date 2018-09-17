
from odoo import models, fields

class ClassScheduler(models.Model):
    _name = "class.scheduler"
    _description = "Class Scheduler"
    
    name = fields.Char(string = 'Classes schedules')
    class_id = fields.Many2one('classes.ept',string='Classes Name')
    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')
    class_calendar_id = fields.Many2one('resource.calendar',string='Class Scheduler')
    employee_ids = fields.Many2many('hr.employee','cls_schedule_employee_rel','cls_schedule_id','employee_id',string = "Employee")
    
