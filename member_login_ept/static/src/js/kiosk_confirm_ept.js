odoo.define('member_login_ept.kiosk_confirm_ept', function (require) {
"use strict";

	var core = require('web.core');
	var Widget = require('web.Widget');
	var utils = require('web.utils');
	var QWeb = core.qweb;
	
	var clk_cls
	
	var KioskConfirmEpt = Widget.extend({
		
		events: {
	        "click .o_hr_attendance_back_button_member": function () { this.do_action(this.next_action, {clear_breadcrumbs: true}); },
	        "click .o_hr_attendance_sign_in_out_icon_member": function () {
	        	this.$('.o_hr_attendance_sign_in_out_icon_member').attr("disabled", "disabled");
	        	this.create_attandance();
	        },
	    },
	
	    init: function (parent, action) {
	        this._super.apply(this, arguments);
	        this.next_action = 'member_login_ept.hr_attendance_action_kiosk_mode_member';
	        this.partner_id = action.partner_id;
	        this.partner_name = action.partner_name;
	        this.partner_state = action.partner_state;
	    },
	
	    start: function () {
	        var self = this;
	        this.getSession().user_has_group('member_login_ept.group_hr_attendance_use_pin').then(function(has_group){
	            var co_cookie  = utils.get_cookie('company_id');
	            self._rpc({
	            	model:'classes.ept',
	            	method:'get_classes',
	            	args:[['id'],co_cookie]
	            }).then(function(result){
//	            	if (result == "False"){
//	            		alert('There are no any classes configure for this time !! Please configure any classes..');
//	            	};
	            	self.use_pin = has_group;
		            self.$el.html(QWeb.render("HrAttendanceKioskConfirmEpt", {widget: self,'result': result }));
		            self.start_clock();
	            	
	            	self.$el.find('.o_hr_attendance_sign_in_out_icon_member').on('click', function(){
	            		clk_cls = $(this).data('class-id')
	            	});
	            });
	        });
	        return self._super.apply(this, arguments);
	    },
	    
	    create_attandance:function(){
	    		var self= this;
	            var cookie  = utils.get_cookie('company_id');
	            
	            self._rpc({
	                    model: 'res.partner',
	                    method: 'attendance_manual',
	                    args: [[self.partner_id], this.next_action, cookie,clk_cls],
	            }).then(function(result) {
	            	if (result.action) {
	            		self.do_action(result.action);
	            	} else if (result.warning) {
	            		self.do_warn(result.warning);
	            		self.$('.o_hr_attendance_sign_in_out_icon_member').removeAttr("disabled");
	            	}
	            });
	    },
	    
	    start_clock: function () {
	        this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));}, 500);
	        // First clock refresh before interval to avoid delay
	        this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));
	    },
	
	    destroy: function () {
	    	clearInterval(this.clock_start);
	        this._super.apply(this, arguments);
	    },
	});
	
	core.action_registry.add('hr_attendance_kiosk_confirm_ept', KioskConfirmEpt);
	
	return KioskConfirmEpt;

});
