odoo.define('website_crm_ept.student_profile', function (require) {
"use strict";
$(document).ready(function(){


	//$('.o_website_form_send').classList.add("student_form");
	
$( function() {
    $( "#dob" ).datepicker({changeMonth: true,
	    changeYear: true,yearRange: "-70:+0",
    	onSelect: function (selected) {
    		
            var dob = new Date(selected);
            var today = new Date();
            
            var age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000));
            var  age_days=Math.floor(((today-dob))/(1000* 60 * 60* 24))
            
            if(age_days < 1279)
            	{
            	alert("Age must be greater then 3.5 year ")
            	$( "#dob" ).val("");
            	}
            if(age_days > 6574 ){
            	
            	$("input[name='parent_name']" ).removeAttr('required');
            	$("input[name='parent_name']" ).val("");
            	$(".parent_name" ).hide();
            }
            else{
            	$(".parent_name" ).show();
            	//$("input[name='parent_name']" ).removeAttr('required');
            	$("input[name='parent_name']" ).attr("required", "true");
            }
         }
    });
    
    
    
    $( "#starting_date" ).datepicker({changeMonth: true,
	    changeYear: true,yearRange: "-70:+20",
	    minDate: 0,
    	onSelect: function (_date, _datepicker) {
            var myDate = new Date(_date);
            var mydate=new Date(myDate.setDate(myDate.getDate()+7))
            var dd = mydate.getDate();
            var mm = mydate.getMonth()+1; //January is 0!
            var yyyy = mydate.getFullYear();
            if(dd<10){
                dd='0'+dd;
            } 
            if(mm<10){
                mm='0'+mm;
            } 
            var today = mm+'/'+dd+'/'+yyyy;
            $('#ending_date').val(today);
            
         }
    });
    
    
    	
  } );

$( "input[name='parent_name']" ).on("focusout",function(){
    var parent_name = $(this).val()
    var parent_name_pattern = /^[a-z," "]+$/i; 
    if (parent_name_pattern.test(parent_name)) {
		$(".parent_name_req").remove();
		}		
    else {
	$(".parent_name_req").remove();	
	$("input[name='parent_name']").val('');
	$("input[name='parent_name']").after( "<span class='parent_name_req'>Alphabets Only</span> ");	
    }
});
});
});
