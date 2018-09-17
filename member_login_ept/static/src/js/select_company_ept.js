odoo.define('member_login_ept.select_company_ept', function (require) {
"use strict";

	var core = require('web.core');
	var Widget = require('web.Widget');
	var Session = require('web.session');
	var utils = require('web.utils'); 
	var QWeb = core.qweb;
	
	var CompanySelectionEpt = Widget.extend({
		 events: {
			 "click .confirm_company": function(){
				 var self = this;
			     $.when(this.get_data()).then(function(){
			    	 self.do_action(self.next_action);
			     }); 
		     },
		 },
		 
	    init: function (parent, action) {
	    	this._super.apply(this, arguments);
	        this.next_action = 'member_login_ept.hr_attendance_action_kiosk_mode_member';
	        utils.set_cookie('company_id',"",-1);
	    },
	    
	    renderElement:function(){
	    	var self = this;
	    	self._super.apply(this, arguments);
        	this._rpc({
                model: 'member.login.ept',
                method: 'get_companies',
                args: [['id']],
            })
            .then(function (companies){
            	var option = ""
            		_.each(companies, function(c){
            		option += "<option value="+c.id+">"+c.name+"</option>"
            	});
                self.$el.html(QWeb.render("HrAttendanceCompanyScreen", {widget: self}));
                $('#company_id').html(option);
            });
	    },
	    
	    get_data:function(){
	    	var co_id;
	    	var get_co_id;
	    	co_id = $('#company_id').val();
	    	utils.set_cookie('company_id', JSON.stringify({'company_id': co_id}), 120*60*60);
	    },
	    
	    destroy: function () {
	        this._super.apply(this, arguments);
	    },

	});

	core.action_registry.add('hr_attendance_company_selection_member', CompanySelectionEpt);

	return CompanySelectionEpt;


});
