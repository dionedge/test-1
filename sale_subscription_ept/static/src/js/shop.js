odoo.define('website_crm_ept.student_profile', function (require) {
"use strict";
$(document).ready(function(){
	var ajax = require('web.ajax');
	var url=window.location.pathname;
	var empty_sign =""
	if(url=="/kaijin_billing_agreement")
	{
		$('.btn-primary').hide();
		
		setInterval(function() {
			$('.o_portal_sign_submit').hide();
			if(empty_sign=="")
				empty_sign = $("#o_portal_signature").jSignature('getData', 'image');
    		}, 1000);
		var today = new Date();
		var dd = today.getDate();
		var mm = today.getMonth()+1; //January is 0!
		var yyyy = today.getFullYear();
		if(dd<10) {
		    dd = '0'+dd
		} 

		if(mm<10) {
		    mm = '0'+mm
		} 

		today = mm + '/' + dd + '/' + yyyy;
		$("#bill_payment_date").val(today);
		$("#service_start_date").val(today);
		$("#service_expiration_date").val(mm + '/' + dd + '/' + (yyyy+1));
		
	}
	if(url=="/shop/cart")
	{
	ajax.jsonRpc('/check_for_service', 'call').then(function (data) 
		{
		if(data)
			{
			$('#checkout_link').hide();
			$('#agreement_link').show();
			}
		else
			{
			$('#checkout_link').show();
			$('#agreement_link').hide();}
		
		});
	
	}
$( "#service_start_date" ).datepicker({changeMonth: true,
    changeYear: true,yearRange: "-70:+20",
    minDate: 0,
	onSelect: function (_date, _datepicker) {
        var myDate = new Date(_date);
        var mydate=new Date(myDate.setDate(myDate.getDate()))
        var dd = mydate.getDate();
        var mm = mydate.getMonth()+1; //January is 0!
        var yyyy = mydate.getFullYear()+1;
        if(dd<10){
            dd='0'+dd;
        } 
        if(mm<10){
            mm='0'+mm;
        } 
        var today = mm+'/'+dd+'/'+yyyy;
        $('#service_expiration_date').val(today);
        
     }
});


$( ".js_billing_agreement_submit" ).click(function() {
	var signature = $("#o_portal_signature").jSignature('getData', 'image');
	var partner_name = $("#o_portal_sign_name").val();
	var sign_ok=$('.o_portal_sign_submit').click();
	 if(signature==empty_sign)
		 alert("empty sign")
     //var signature = $("#o_portal_signature").jSignature('getData', 'image');
     var is_empty = signature ? empty_sign[1] === signature[1] : true;
     if(is_empty)
    	 return false;
     else
    	 $( "#kaijin_billing_form" ).submit();
});
	




	
	
});
});