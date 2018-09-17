from odoo import api, fields, models, _ , tools
import datetime as dt
import pytz

class Member_attendance_report(models.Model):
    _name= 'member.attandance.report.ept'
    _auto = False
    
    class_id = fields.Many2one('classes.ept',string='Classes',readonly=True)
    member_attendance_hours = fields.Float('Hours Attended in Class',readonly=True)
    class_member_avg_attendance_hours = fields.Float('Class Average of Hours Attended',readonly=True)
    attendance_week = fields.Char('Week')
    attendance_month = fields.Selection([
        (1, 'January'), (2, 'Febuary'),(3, 'March'),
        (4, 'April'), (5, 'May'),(6, 'June'),
        (7, 'July'),(8, 'August'),(9, 'Septmember'),
        (10, 'October'),(11, 'November'),(12, 'December')],
        string="Month")
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
                
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            
            select row_number() OVER () AS id,table1.class_id as class_id
            ,table1.member_total_attendance as member_attendance_hours
            ,table2.Average_Hours as class_member_avg_attendance_hours,
             'Week - ' || EXTRACT(Week FROM table1.week) as attendance_week,
            EXTRACT(MONTH FROM table1.week) as attendance_month
            
            from
            (select cls.id as class_id,ROUND((EXTRACT(epoch FROM sum(check_out - check_in))/3600)::numeric,2) as 
            member_total_attendance,date_trunc('week', check_in) as week,date_trunc('month', check_in)
            
            from member_login_ept mem join classes_ept cls
             on mem.class_id = cls.id where partner_id = %s group by cls.id 
             ,date_trunc('week', check_in),date_trunc('month', check_in)
             
            )table1 inner join
            (select cls.id as class2,
            round(((EXTRACT(epoch FROM sum(check_out - check_in))/3600)/count(*))::numeric,2)
            as Average_Hours, 
            date_trunc('week', check_in) as week
            
            from member_login_ept mem join classes_ept cls
             on mem.class_id = cls.id group by cls.id
             ,date_trunc('week', check_in)
             
            )table2 
            on table1.class_id = table2.class2 where table1.week = table2.week group by table1.class_id,table1.member_total_attendance,
            table2.Average_Hours,table1.week
            

            
        )""" % (
                    self._table,self.env.user.partner_id.id))
