# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Account Ept',
    'version' : '1.1',
    'summary': 'Create a new module',
    'sequence': 30,
    'description': """
     Added some accounting features. 
         
    """,
    'category': '',
    'website': 'www.emiprotechnologies.com',
    'depends' : ['account'],
    'data': [
        'views/account_journal_ept.xml',
        'views/account_invoice_ept.xml',
        'wizard/freeze_reason.xml',
        'views/mail_template_data.xml',
        'views/web_assets_ept.xml',
        'data/active_invoice.xml'
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
