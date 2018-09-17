# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Menu Setting Ept',
    'version' : '11.0',
    'category': '',
    'summary': 'Groups for Admin',
    'sequence': 30,
    'description': """
        Group for hiding menu of base.
    """,

    'website': 'https://www.emiprotechnologies.com',
    'author' : 'Emipro Technologies Pvt Ltd',
    
    'depends' : ['base'],
    'data': [
            'views/menu_setting_ept.xml',
     ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
