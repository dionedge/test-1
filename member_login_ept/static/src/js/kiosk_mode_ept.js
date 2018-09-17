odoo.define('member_login_ept.kiosk_mode_ept', function (require) {
"use strict";

	var core = require('web.core');
	var Widget = require('web.Widget');
	var Session = require('web.session');
	var utils = require('web.utils'); 
	var QWeb = core.qweb;
	
	var KioskModeEpt = Widget.extend({
	    events: {
	        "click .o_hr_attendance_button_member": function(){ this.do_action('member_login_ept.hr_employee_attendance_action_kanban_member');
	        //here code for clear previous breadcumbs.. of company_selections
	        },
	    },
	
	    start: function () {
	        var self = this;
	        self.session = Session;
	        var cookie  = jQuery.parseJSON(utils.get_cookie('company_id')).company_id;
	        this._rpc({
	                model: 'res.company',
	                method: 'search_read',
	                args: [[['id', '=',  cookie]], ['name']],
	            })
	            .then(function (companies){
	                self.company_name = companies[0].name;
	                self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: cookie, field: 'logo',});
	                self.$el.html(QWeb.render("HrAttendanceKioskModeEpt", {widget: self}));
	                self.start_clock();
	            });
	        return self._super.apply(this, arguments);
	    },
	
	    start_clock: function() {
	        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock_ept").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));}, 500);
	        // First clock refresh before interval to avoid delay
	        this.$(".o_hr_attendance_clock_ept").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));
	    },
	
	    destroy: function () {
	        clearInterval(this.clock_start);
	        this._super.apply(this, arguments);
	    },
	});
	
	core.action_registry.add('hr_attendance_kiosk_mode_member', KioskModeEpt);
	
	return KioskModeEpt;
	
});
