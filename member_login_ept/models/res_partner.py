
import ast

from odoo import models,fields,api,exceptions

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    attendance_ids = fields.One2many('member.login.ept', 'partner_id', help='list of attendances for the partner')
    last_attendance_id = fields.Many2one('member.login.ept', compute='_compute_last_attendance_id_ept')
    attendance_state = fields.Selection(string="Attendance", compute='_compute_attendance_state_ept', selection=[('checked_out', "Checked out"), ('checked_in', "Checked in")])
    active_member = fields.Boolean("Active member")
    
    @api.depends('attendance_ids')
    def _compute_last_attendance_id_ept(self):
        for parnter in self:
            parnter.last_attendance_id = parnter.attendance_ids and parnter.attendance_ids[0] or False
 
    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_state_ept(self):
        for parnter in self:
            parnter.attendance_state = parnter.last_attendance_id and not parnter.last_attendance_id.check_out and 'checked_in' or 'checked_out'
   
    @api.multi
    def attendance_manual(self, next_action, get_cookie,get_class):
        self.ensure_one()
        cookie_dict_vals = ast.literal_eval(get_cookie)
        co_id_cookie = int(cookie_dict_vals.get('company_id'))
        return self.attendance_action(next_action,co_id_cookie,get_class) 
    
    @api.multi
    def attendance_action(self, next_action,co_id_cookie,get_class):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        action_message = self.env.ref('member_login_ept.hr_attendance_action_greeting_message_member').read()[0]
        action_message['previous_attendance_change_date'] = self.last_attendance_id and (self.last_attendance_id.check_out or self.last_attendance_id.check_in) or False
        action_message['partner_id.name'] = self.name
        action_message['next_action'] = next_action

        if self.user_id:
            modified_attendance = self.sudo(self.user_id.id).attendance_action_change(co_id_cookie,get_class)
        else:
            modified_attendance = self.sudo().attendance_action_change(co_id_cookie,get_class)
        action_message['attendance'] = modified_attendance.read()[0]
        return {'action': action_message}
            
    @api.multi
    def attendance_action_change(self,co_id_cookie,get_class):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))
        action_date = fields.Datetime.now()

        if self.attendance_state != 'checked_in':
            vals = {
                'partner_id': self.id,
                'company_id':co_id_cookie,
                'check_in': action_date,
                'class_id':get_class
            }
            return self.env['member.login.ept'].create(vals)
        else:
            attendance = self.env['member.login.ept'].search([('partner_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(partner_id.name)s, could not find corresponding check in. '
                    'Your attendances have probably been modified manually by human resources.') % {'partner_id.name': self.name, })
            return attendance
    
