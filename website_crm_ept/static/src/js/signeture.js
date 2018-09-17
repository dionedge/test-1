odoo.define('portal.signature_form', function (require){
    "use strict";
    require('web_editor.ready');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var core = require('web.core');
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");

    var qweb = core.qweb;

    
    var SignatureForm = require('portal.signature_form').SignatureForm;
    SignatureForm.include({
    	events: {
    		'click #o_portal_sign_clear': 'clearSign',
            'click .o_portal_sign_submit': 'submitSign',
            'init #o_portal_sign_accept': 'initSign',
    		'change #sign_img': function(e) {
    			this.$("#o_portal_signature").jSignature('reset');
    			var image = new Image;
    			var $canvas = $(".jSignature");
                var context = $canvas[0].getContext("2d");
                //context.drawImage(this, 10, 10);
                var URL = window.URL;
                var url = URL.createObjectURL(e.target.files[0]);
                image.src =url
                image.onload = function() {
                    context.drawImage(image,10,0,250,100);
                    $(".jSignature")("disable");
                }
    		} ,
    		'click .o_sign_mode_auto': function(e) {
    			this.$("#o_portal_signature").jSignature('reset');
    			var partner_name=$('#o_portal_sign_name').val();
    			var $canvas = $(".jSignature");
                var context = $canvas[0].getContext("2d");
                console.log(context)
                context.font = '40px sans-serif';
                context.fillStyle ="black";
                context.fillText(partner_name, 50,100);
                $("#o_portal_signature").jSignature('disable');
    		},
    		'click .o_sign_mode_draw': function(e) {
    			this.$("#o_portal_signature").jSignature('reset');
                $("#o_portal_signature").jSignature('enable');
    		},
    	 },
    	 _loadTemplates: function () {
    	   	 return $.when(this._super(), ajax.loadXML('/website_crm_ept/static/src/xml/signature.xml', qweb));
    	    },
    	    start: function() {
    	    	this._super();
                //return $.when(this._super.apply(this, arguments));
                ajax.jsonRpc('/sign/get_fonts', 'call', {}).then(function(data) {
                	SignatureForm.fonts = data;
                });
                
    	    },
	 
    });
});