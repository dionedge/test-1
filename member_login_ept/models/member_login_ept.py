
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api, exceptions, _
from datetime import datetime
import datetime as dt
import pytz
import logging
_logger = logging.getLogger(__name__)

class MemberLoginEpt(models.Model):
    _name = "member.login.ept"
    _description = "Member Login"

    @api.depends('check_in', 'check_out')
    def  _compute_worked_hours(self):
        for attendance in self:
            if attendance and attendance.check_out and attendance.check_in:
                delta = datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                attendance.worked_hours = delta.total_seconds() / 3600.0
                    
    partner_id = fields.Many2one('res.partner',string='Partner',required=True)
    instructure_id = fields.Many2many('hr.employee',string='Instructure')
    company_id = fields.Many2one('res.company',string="Company")
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    timesheet_id = fields.Many2one('timesheet.ept',string='Timesheet',compute='_compute_timesheet',store=True)
    worked_hours = fields.Float(string='Worked Hours',compute='_compute_worked_hours')
    check_in = fields.Datetime(string='Check In', default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string='Check Out')
    class_id = fields.Many2one('classes.ept', string='Class Name')
    
    @api.model
    def members_auto_check_out(self):
        """This method is execute by cron job. this method is use for auto sign out of employee and instructors."""
        attendance_ids = self.env['member.login.ept'].search([
            ('check_in', '<=', fields.Datetime.now()),
            ('check_out', '=', False),('class_id','!=',False)
            ])
          
        tz=pytz.timezone('America/New_York')
        if self._uid:
            user=self.env['res.users'].browse(self._uid)
        if user and user.tz:
            tz=pytz.timezone(user.tz)
        current_utc_date_time= dt.datetime.utcnow()
        current_date_time = current_utc_date_time.replace(tzinfo=pytz.utc).astimezone(tz)
        current_date = datetime.strftime(current_date_time, '%Y-%m-%d')   
        current_time = datetime.strftime(current_date_time, '%H:%M:%S')
        current_day = current_date_time.weekday()
        split_time = [int(n) for n in current_time.split(":")]
        current_time_float_val = split_time[0] + split_time[1]/60.0 
        for attendance_id in attendance_ids:
            is_member_sign_out = True
            class_schedule_ids = self.env['class.scheduler'].search([
                ('from_date', '<=', current_date),('class_id', '=', attendance_id.class_id.id),
                ('to_date', '>=', current_date)
                ])
            
            for scheduler_id in class_schedule_ids:
                class_calendar_id = scheduler_id.class_calendar_id
                if class_calendar_id:
                    cal_att_id = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(current_day)),('calendar_id','=',class_calendar_id.id)])
                    if self.env['resource.calendar.attendance'].search([('dayofweek','=',str(current_day)),('calendar_id','=',class_calendar_id.id),
                                                                        ('hour_from','<=',current_time_float_val),('hour_to','>=',current_time_float_val)]):
                                                                    
                        is_member_sign_out = False
                        
                    else:
                        for attendance_id in self.env['hr.attendance'].search([('employee_id','in',scheduler_id.employee_ids.ids),('class_id','=',scheduler_id.class_id.id),
                                                                              ('check_in', '<=', fields.Datetime.now()),('check_out','=',False)]) :
                            sign_in_time = datetime.strptime(attendance_id.check_in, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc).astimezone(tz).strftime('%H:%M:%S')
                            sign_in_time_split = [int(n) for n in sign_in_time.split(":")]
                            sign_in_time_float_val = sign_in_time_split[0] + sign_in_time_split[1]/60.0
                            
                            try:
                                cal_att_id = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(current_day)),('calendar_id','=',class_calendar_id.id),
                                                                        ('hour_from','<=',sign_in_time_float_val),('hour_to','>=',sign_in_time_float_val)])
                                if cal_att_id:
                                    minutes = cal_att_id[0].hour_to * 60
                                    hours, minutes = divmod(minutes, 60)
                                    from_time = dt.datetime.strptime("%02d:%02d"%(hours,minutes),'%H:%M').time()
                                    sign_out_date_time = dt.datetime.combine(current_date_time.date(),from_time)
                                    local_sign_in_time = tz.localize(sign_out_date_time, is_dst=None)
                                    sign_out_date_time = dt.datetime.strftime(local_sign_in_time.astimezone (pytz.utc), '%Y-%m-%d %H:%M:%S')
                                    attendance_id.write({'check_out':sign_out_date_time})
                                else:
                                    attendance_id.write({'check_out':fields.Datetime.now()})
                                    self._cr.commit()
                            except Exception as e:
                                _logger.info("=======Exception while create sign in of employee :- %s and Exception :- %s" %(attendance_id.employee_id.name,e))
                                pass
                        
            if is_member_sign_out and attendance_id.check_in and not attendance_id.check_out:
                try:
                    attendance_id.check_out = fields.Datetime.now()
                    self._cr.commit()
                except Exception as e:       
                    _logger.info("=======Exception while create sign out of Member :- %s and Exception :- %s" %(attendance_id.partner_id.name,e))
                    pass       
                                
                
    @api.multi
    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.check_out:
                result.append((attendance.id, _("%(partner_id.name)s from %(check_in)s") % {
                    'partner_id.name': attendance.partner_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_in))),
                }))
            else:
                result.append((attendance.id, _("%(partner_id.name)s from %(check_in)s to %(check_out)s") % {
                    'partner_id.name': attendance.partner_id.name,
                    'check_in': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_in))),
                    'check_out': fields.Datetime.to_string(fields.Datetime.context_timestamp(attendance, fields.Datetime.from_string(attendance.check_out))),
                }))
        return result
    
    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.multi
    def copy(self):
        raise exceptions.UserError(_('You cannot duplicate an attendance.'))
    
    @api.constrains('check_in', 'check_out', 'partner_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['member.login.ept'].search([
                ('partner_id', '=', attendance.partner_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(partner_id.name)s, the employee was already checked in on %(datetime)s") % {
                    'partner_id.name': attendance.partner_id.name,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })

            if not attendance.check_out:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['member.login.ept'].search([
                    ('partner_id', '=', attendance.partner_id.id),
                    ('check_out', '=', False),
                    ('id', '!=', attendance.id),
                ])
                if no_check_out_attendances:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(partner_id.name)s, the employee hasn't checked out since %(datetime)s") % {
                        'partner_id.name': attendance.partner_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
                    })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['member.login.ept'].search([
                    ('partner_id', '=', attendance.partner_id.id),
                    ('check_in', '<', attendance.check_out),
                    ('id', '!=', attendance.id),
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(_("Cannot create new attendance record for %(partner_id.name)s, the employee was already checked in on %(datetime)s") % {
                        'partner_id.name': attendance.partner_id.name,
                        'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
                    })
    
    @api.multi
    def get_companies(self):
        companies = self.env.user.company_ids
        return [{'id': company.id, 'name': company.name} for company in companies ]
                        
    @api.model
    def employee_auto_check_in(self):
        """This method is executed by cron. this method will auto check in of class instructor."""
        tz=pytz.timezone('America/New_York')
        if self._uid:
            user=self.env['res.users'].browse(self._uid)
        if user and user.tz:
            tz=pytz.timezone(user.tz)
        current_utc_date_time= dt.datetime.utcnow()
        current_date_time = current_utc_date_time.replace(tzinfo=pytz.utc).astimezone(tz)
        current_utc_date_time_str = datetime.strftime(current_utc_date_time, '%Y-%m-%d %H:%M:%S')
#         current_date = datetime.strftime(current_date_time, '%Y-%m-%d %H:%M:%S')   
        current_time = datetime.strftime(current_date_time, '%H:%M:%S')
        current_day = current_date_time.weekday()
        split_time = [int(n) for n in current_time.split(":")]
        current_time_float_val = split_time[0] + split_time[1]/60.0
        
        self._cr.execute("""select distinct class_id from member_login_ept where check_in::date = '%s' and check_out is null""" %(current_utc_date_time.date()))
        class_ids = [r[0] for r in self._cr.fetchall()]
        for class_id in self.env['classes.ept'].browse(class_ids):
            class_schedule_ids = self.env['class.scheduler'].search([
                    ('from_date', '<=', current_utc_date_time_str),('class_id', '=', class_id.id),
                    ('to_date', '>=', current_utc_date_time_str),('class_calendar_id','!=',False),('employee_ids','!=',False)
                    ])
            
            for cls_schedule_id in class_schedule_ids:
                calender_attendance_id = self.env['resource.calendar.attendance'].search([('dayofweek','=',str(current_day)),('calendar_id','=',cls_schedule_id.class_calendar_id.id),
                                                                             ('hour_from','<=',current_time_float_val),('hour_to','>=',current_time_float_val)])
                if calender_attendance_id and calender_attendance_id[0].hour_from:
                    minutes = calender_attendance_id[0].hour_from * 60
                    hours, minutes = divmod(minutes, 60)
                    from_time = dt.datetime.strptime("%02d:%02d"%(hours,minutes),'%H:%M').time()
                    sign_in_date_time = dt.datetime.combine(current_date_time.date(),from_time)
                    local_sign_in_time = tz.localize(sign_in_date_time, is_dst=None)
                    sign_in_date_time = dt.datetime.strftime(local_sign_in_time.astimezone (pytz.utc), '%Y-%m-%d %H:%M:%S')
                    for employee_id in cls_schedule_id.employee_ids: 
                        
                        if not self.env['hr.attendance'].search([('employee_id','=',employee_id.id),('check_in','>=',sign_in_date_time),('check_in','<=',current_utc_date_time_str),('check_out','=',False)]):
                            try:
                                self.env['hr.attendance'].create({'employee_id':employee_id.id,'check_in':sign_in_date_time,'class_id':class_id.id})
                                self._cr.commit()
                               
                            except Exception as e:
                                _logger.info("=======Exception while create sign in of employee :- %s and Exception :- %s" %(employee_id.name,e))
                                pass 
                    break
    @api.model
    def member_absent_mail_notify(self):
        current_date = dt.date.today()
        template_id=int(self.env['ir.config_parameter'].get_param('truancy_report_mail_template_id')) or False,
        template_id = template_id and self.env['mail.template'].browse(template_id) or False
        number_of_days=int(self.env['ir.config_parameter'].get_param('truancy_report_number_of_days')) or False
        if template_id and number_of_days:
            notify_date = current_date - dt.timedelta(days=number_of_days) 
            self._cr.execute("""select partner_id,check_in as date,class,id from (select distinct on (partner_id) partner_id,check_in,class_id as class,id 
                                from member_login_ept order by partner_id,class_id,check_in::date desc)tmp
                                where check_in::date < '%s'""" %(notify_date))  
#             self._cr.execute("""select partner_id,check_in as date,class,id from (select distinct on (partner_id,class_id) partner_id,check_in,class_id as class,id 
#                                 from member_login_ept order by partner_id,class_id,check_in::date desc)tmp
#                                 where check_in::date < '%s'""" %(notify_date))  
            res = self._cr.fetchall()
            for record in  res:
                if len(record)>2 and record[2]:
                    
                    recipient_ids = []
                    for instructor in self.env['classes.ept'].browse(record[2]) and self.env['classes.ept'].browse(record[2]).instructors_emplyees_ids:
                        recipient_ids.append(instructor.user_id and instructor.user_id.partner_id and instructor.user_id.partner_id.id or False)
#                     template_id['email_from'] = "email"
#                     template_id['res_id'] = record[3]
                    template_id['email_to'] = recipient_ids and ','.join(str(e.email) for e in self.env['res.partner'].browse(recipient_ids)) or False
                    if not template_id['email_to'] and not template_id['email_from']:
                        pass
                    template_id.send_mail(record[3])
            return True
                
                
