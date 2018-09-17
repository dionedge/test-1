odoo.define('adptive_theme.top_fix_header', function (require) {
"use strict";
$(document).ready(function(){
	window.onscroll = function() {fix_header()};

	var navbar = $(".nav_bar > .container");
	var sticky = navbar.offsetTop;

	function fix_header() {
	  if (window.pageYOffset >= sticky) {
	    navbar.addClass( "sticky" );
	  } else {
		  navbar.removeClass( "sticky" );
	  }
	}
	
	
});
});