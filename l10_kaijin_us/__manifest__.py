# -*- coding: utf-8 -*-
{
    'name' : 'Chart Of Account(KAIJIN US)',
    'version' : '11.0',
    'summary': '',
    'sequence': 1,
    
    'description': """

    """,
    'author': 'Emipro Technologies Pvt. Ltd.',    
    'category': '',
    'website': 'http://www.emiprotechnologies.com/',
    'images' : [],
    'depends' : ['account_invoicing'],
    'data': [ 
         'data/kaijin_us_chart_data.xml',
         'data/account.account.template.csv',
         'data/account_chart_template_data.yml',                   
    ],      
    'installable': True,
    'application': False,
    'auto_install': False,
}
