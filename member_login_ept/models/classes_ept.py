
from odoo import models, fields, api
from datetime import datetime
import ast

class ClassesEpt(models.Model):
    _name = "classes.ept"
    _description = "Classes Ept"
    
    name = fields.Char(string='Name')
    instructors_emplyees_ids = fields.Many2many('hr.employee',string='Instructors')
    company_id = fields.Many2one('res.company',string='Company')
    class_scheduler_ids = fields.One2many('class.scheduler','class_id',srting='Schedulers')
    
    @api.multi
    def get_classes(self,company_cookie):
          
        same_co_class= []
        res = []
        current_date_time= fields.Datetime.now()
        check_in_date = datetime.strptime(current_date_time, '%Y-%m-%d %H:%M:%S').date()
        check_in_dayname = str(check_in_date.weekday()+1)
         
        self._cr.execute("""select distinct cl.id
            from classes_ept cl 
            join class_scheduler cs on cl.id = cs.class_id
            join resource_calendar rc on rc.id = cs.class_calendar_id
            join resource_calendar_attendance rca on rca.calendar_id = rc.id
            where now() BETWEEN cs.from_date and cs.to_date
            and extract(dow from current_date) = %s
            --and extract('hour' from current_time) between rca.hour_from and rca.hour_to
            and EXTRACT(epoch FROM (to_char(NOW(), 'HH24:MI:SS')::time)) / 3600 between rca.hour_from and rca.hour_to
            """%(check_in_dayname))
          
        classes_happening = self._cr.fetchall()
        if classes_happening:
            for ch in classes_happening:
                res.append(ch[0])
             
        cls_obj = self.env['classes.ept'].browse(res)
        cookie_dict_vals = ast.literal_eval(company_cookie)
        co_id_cookie = int(cookie_dict_vals.get('company_id'))
          
        for cls in cls_obj:
            if cls.company_id.id == co_id_cookie:
                same_co_class.append(cls)
         
        if  same_co_class:
            return [{'id': scc.id, 'name':scc.name} for scc in same_co_class]
   
