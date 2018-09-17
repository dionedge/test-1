odoo.define('website_crm_ept.student_profile', function (require) {
"use strict";
$(document).ready(function(){
	 var url=window.location.pathname;
	 var ajax = require('web.ajax');
	 var core = require('web.core');
	 var base = require('web_editor.base');
	 var _t = core._t;
	 var qweb = core.qweb;
	 var rpc = require("web.rpc");
	 var Widget = require("web.Widget");
	if(url=="/shop/cart")
		{
		ajax.jsonRpc('/check_for_service', 'call').then(function (data) 
			{
			if(data)
				{$('#checkout_link').hide();}
			else
				{$('#checkout_link').show();}
			});
		
		}
});
});