
from odoo import models, fields, api

class TimesheetEpt(models.Model):
    _name = "timesheet.ept"
    _description = "Timesheet"
    _rec_name = "partner_id"
    
    attendance_ids = fields.One2many('member.login.ept','timesheet_id',string='Attendance')
    partner_id = fields.Many2one('res.partner',string='Partner',required=True)
    company_id = fields.Many2one('res.company',string='Company')
    from_date = fields.Datetime(string='From Date', default=fields.Datetime.now)
    to_date = fields.Datetime(string='To Date')
    total_attendance = fields.Float(string='Total Attendance',compute='_compute_total_attendance')
    current_status = fields.Selection(string='Current Status',selection=[('absent', "Absent"), ('present', "Present")])
    
    @api.onchange('partner_id')
    def onchange_partener_id(self):
        self.company_id = self.partner_id.company_id.id    
    
    @api.multi
    def _compute_total_attendance(self):
        sum_total = 0
        for attendance in self.attendance_ids:
            sum_total = sum_total + attendance.worked_hours
        self.total_attendance = sum_total
        return sum_total
    
    @api.model
    def create(self, vals):
        vals = self._timesheet_preprocess(vals)
        return super(TimesheetEpt, self).create(vals)
    
    @api.multi
    def write(self, vals):
        vals = self._timesheet_preprocess(vals)
        return  super(TimesheetEpt, self).write(vals)
    
    def _timesheet_preprocess(self, vals):
        """ Deduce other field values from the one given.
            Overrride this to compute on the fly some field that can not be computed fields.
            :param values: dict values for `create`or `write`.
        """

        # employee implies user
        if vals.get('partner_id') and not vals.get('user_id'):
            employee = self.env['res.partner'].browse(vals['partner_id'])
            vals['user_id'] = employee.user_id.id
        return vals

     
    
