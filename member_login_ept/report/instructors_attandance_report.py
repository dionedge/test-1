
from odoo import api, fields, models, _ , tools
import pytz

class instructor_report(models.Model):
    _name= 'instructor.attandance.report.ept'
    _auto = False
    
    date_from = fields.Date("Date From",readonly=True)
    date_to = fields.Date("Date To",readonly=True)
    employee_id = fields.Many2one('hr.employee',string='Instructors',readonly=True)
    week_day = fields.Char("Day")
    check_in_time = fields.Datetime("Check In",readonly=True)
    check_out_time = fields.Datetime("Check Out",readonly=True)
    worked_hours = fields.Float("Worked Hours",readonly=True)
    class_id = fields.Many2one('classes.ept',"Class") 
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        self.env.cr.execute("""
                CREATE or REPLACE VIEW %s as (
                    select row_number() OVER () AS id,sheet.date_from AS date_from,sheet.date_to AS date_to,att.class_id as class_id,
                            sheet.employee_id AS employee_id,att.check_in AS check_in_time,
                            att.check_out AS check_out_time,
                            to_char(att.check_in, 'Day') AS week_day,
                            round(att.worked_hours::numeric,2) AS worked_hours from 
                            hr_timesheet_sheet_sheet sheet inner join
                            hr_attendance att on sheet.id = att.sheet_id 
                            join class_scheduler cs on cs.class_id = att.class_id
                            join cls_schedule_employee_rel cls_sh_emp_rel on cs.id = cls_sh_emp_rel.cls_schedule_id
                            where att.check_in BETWEEN cs.from_date and cs.to_date and cls_sh_emp_rel.employee_id = sheet.employee_id
                           order by att.check_in
                            )
                            """
                            % (
                                self._table))
     
