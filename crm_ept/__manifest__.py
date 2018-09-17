# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Crm Ept',
    'version' : '11.0',
    'summary': '',
    'sequence': 30,
    
    'author':'Emipro Technologies',
    'website': ' www.emiprotechnologies.com',

    'depends' : ['crm','mail'],
    'data': [
        
            'views/res_config_settings.xml',
            'wizard/crm_lead_to_oppo_ept.xml',
            'data/crm_cron.xml', 
            'data/crm_stage_data.xml',
            'views/mail_template.xml'
#             'security/ir.model.access.csv'
             
     ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
