odoo.define('member_login_ept.my_attendances_ept', function (require) {
"use strict";

	var core = require('web.core');
	var Widget = require('web.Widget');
	
	var QWeb = core.qweb;
	var _t = core._t;
	
	
	var MyAttendancesEpt = Widget.extend({
	    events: {
	        "click .o_hr_attendance_sign_in_out_icon_member": function() {
	            this.update_attendance();
	        },
	    },
	
	    start: function () {
	        var self = this;
	
	        this._rpc({
	                model: 'hr.employee',
	                method: 'search_read',
	                args: [[['user_id', '=', self.getSession().uid]], ['attendance_state', 'name']],
	            })
	            .then(function (res) {
	                if (_.isEmpty(res) ) {
	                    self.$('.o_hr_attendance_employee').append(_t("Error : Could not find employee linked to user"));
	                    return;
	                }
	                self.employee = res[0];
	                self.$el.html(QWeb.render("HrAttendanceMyMainMenuEpt", {widget: self}));
	            });
	
	        return this._super.apply(this, arguments);
	    },
	
	    update_attendance: function () {
	        var self = this;
	        this._rpc({
	                model: 'res.partner',
	                method: 'attendance_manual',
	                args: [[self.employee.id], 'member_login_ept.hr_attendance_action_my_attendances_member'],
	            })
	            .then(function(result) {
	                if (result.action) {
	                    self.do_action(result.action);
	                } else if (result.warning) {
	                    self.do_warn(result.warning);
	                }
	            });
	    },
	});
	
	core.action_registry.add('hr_attendance_my_attendances_member ', MyAttendancesEpt);
	
	return MyAttendancesEpt;

});
