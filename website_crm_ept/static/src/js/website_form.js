odoo.define('website_form.animation', function (require) {
'use strict';
$(document).ready(function(){
    
    var core = require('web.core');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var _t = core._t;
    var qweb = core.qweb;
    var timer
    var sAnimation = require('website.content.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb;
    $('.form_waiver').attr('disabled',true);
    $( "input[name='otp']" ).attr('disabled',true);
    $(".send_otp").click(function(){
    	//Disable all other fields
    	$('.send_otp').hide()
    	$( "input[name='contact_name']" ).attr('disabled',true);
    	$( "input[name='email_from']" ).attr('disabled',true);
    	$( "input[name='otp']" ).attr('disabled',false);
        var mail_id=$("input[name='email_from']").val();
        var name = $("input[name='contact_name']").val();
        if(!(mail_id && name))
        	{
        		alert('Enter name and email id')
        	}
        else{
        ajax.jsonRpc('/send_otp', 'call', {'mail_id': mail_id,'name':name}).then(function (data) {
            if(data){
            	$('#otp_key').val(data);
                var counter = 120;
                timer = setInterval(function() {
                		counter--;
                		var str = ("0" + parseInt(counter / 60)).slice(-2)+ ':' + ("0" +(counter % 60)).slice(-2)
                		if (counter >= 0) {
                			$(".timer").remove();
                		$( "<p class='timer'>"+str+"</p>" ).insertAfter( '#otp' );
                		}
                		if (counter === 0) {
                			ajax.jsonRpc('/send_otp_timeout', 'call',{'mail_id': mail_id,'otp_key':data}).then(function (data) 
        							{
        						alert("Your otp is expired , try again");
        						window.location.reload();
        						});
                		}
                		}, 1000);
            }
            else{window.location.reload();}
            })
        }
    })
     $('#otp').on("cut copy paste",function(e) {
      e.preventDefault();
   });
    
    $( "input[name='otp']" ).on("focusout",function(){
        var otp = $(this).val();
        var mail_id=$("input[name='email_from']").val();
        var otp_key=$("#otp_key").val();   
        var otp_pattern =  /^[0-9]{6}$/; 
        if (otp_pattern.test(otp)) {
    		$(".otp").remove();
    		ajax.jsonRpc('/send_otp_check', 'call',{'mail_id': mail_id,'otp_key':otp_key,'otp':otp}).then(function (data) 
    			{
    			if(!(data)){alert("Your otp is not Match , try again");}
    			else{$('.form_waiver').attr('disabled',false);clearInterval(timer);}
    			});
    		}
        else {
    	$(".otp").remove();	
    	$("input[name='otp']").val('');
    	$("input[name='otp']").after( "<span class='otp'>Enter 6 digits Only</span> ");
        }
    	});
    
	sAnimation.registry.form_builder_send.include({
        send: function (e) {
        	$( "input[name='contact_name']" ).attr('disabled',false);
        	$( "input[name='email_from']" ).attr('disabled',false);
        	var model_name=this.$target.data('model_name');
        	var student_form=$('#student_form').val();
        	if (model_name=="crm.lead"  && student_form=="True"){
			var response = grecaptcha.getResponse();
			if (response.length == 0) {
				$(".captcha").remove();
				$('.o_website_form_send').before( "<span class='captcha'>Enter valid captcha</span> ");
				return false
			} else {
					this._super(e);
					$(".captcha").remove();	
					return true
			}
        	}
        	else
        		{
        		this._super(e);     		
        		}
    }
});
});     
});
