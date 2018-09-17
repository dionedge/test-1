from odoo import api, fields, models, _ , tools
import datetime as dt
import pytz

class Class_attendance_report(models.Model):
    _name= 'class.attandance.report.ept'
    _auto = False
    
    class_id = fields.Many2one('classes.ept',string='Classes',readonly=True)
    employee_id = fields.Many2one('hr.employee',string='Instructors',readonly=True)
    
    from_time = fields.Float("From Time",readonly=True)
    to_time = fields.Float("To Time",readonly=True)
    total_member_attendances = fields.Integer('Total Members',readonly=True)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
                
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            
            select row_number() OVER () AS id,count(att.id) AS total_member_attendances,
            cls_sh_emp_rel.employee_id AS employee_id,cls.id AS class_id,cal_att.hour_from AS from_time,cal_att.hour_to 
            as to_time from 
            classes_ept cls 
            inner join 
            class_scheduler cls_sh on cls.id = cls_sh.class_id inner join cls_schedule_employee_rel cls_sh_emp_rel on  
            cls_sh.id = cls_sh_emp_rel.cls_schedule_id inner join 
            resource_calendar cal on cls_sh.class_calendar_id = cal.id inner join resource_calendar_attendance cal_att on 
            cal.id = cal_att.calendar_id left join member_login_ept att on att.class_id = cls.id
            where cls_sh.from_date::date <= timezone('utc', now())::date and 
            cls_sh.to_date::date >= timezone('utc', now())::date
            and cal_att.hour_from <= extract(hour from timezone('utc', now())) + (extract(minutes from timezone('utc', now()))/60)
            and cal_att.hour_to >= extract(hour from timezone('utc', now())) + (extract(minutes from timezone('utc', now()))/60)
            and cal_att.dayofweek = extract(dow from timezone('utc', now())::date - 1)::char
           and att.check_in::date = timezone('utc', now())::date
           and att.check_out is null
            group by cls.id,cls_sh_emp_rel.employee_id,cls_sh.name,cal_att.dayofweek,cal_att.hour_from,cal_att.hour_to

            
        )""" % (
                    self._table))
