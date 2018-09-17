odoo.define('website_crm_ept.student_profile', function (require) {
"use strict";
$(document).ready(function(){
	var url=window.location.pathname;
	if(url=="/contactus")
	{
	$.getJSON("http://ip-api.com/json/?callback=?", function(data) {
            $("#country").val(data.countryCode);
            $("#state").val(data.regionName);
            $("#city").val(data.city);
            $("#zip").val(data.zip);
    });
	}
var ajax = require('web.ajax');
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
$("#filled_date").val(today);


$( "input[name='email_from']" ).on("focusout",function(){
    var e_mail = $(this).val() 
    var e_mail_pattern =  /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/i; 
    if (e_mail_pattern.test(e_mail)) {
	$(".e_mail").remove();
	}
    else {
		$(".e_mail").remove();
		$("input[name='email_from']").val('');
		$("input[name='email_from']").after( "<span class='e_mail'>Enter valid E-mail</span> ");
    }
});

$( "input[name='phone']" ).on("focusout",function(){
    var phone = $(this).val();
    var phone_pattern =  /^[0-9]+$/; 
    if (phone_pattern.test(phone)) {
		$(".phone").remove();
		}
    else {
	$(".phone").remove();	
	$("input[name='phone']").val('');
	$("input[name='phone']").after( "<span class='phone'>Enter digits Only</span> ");
    }
});
});
});
