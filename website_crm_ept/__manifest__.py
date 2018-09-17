# -*- coding: utf-8 -*-
{
    'name': 'Student Profile Acknowledgment & Release ',
    'version': '1.0', 
    'author':'Emipro Technologies',
    'category': 'Website',
    'website': ' www.emiprotechnologies.com',
    'description': "",
    'depends': ['website','website_crm', 'adptive_snippets', 'menu_setting_ept'],
    'data': [
          'security/ir.model.access.csv',
          'views/mail_template_data.xml',
          'views/crm_lead_views.xml',
          'templates/assets.xml',
          'templates/student_profile.xml', 
          'templates/contact_us.xml',
          'views/kaijin_waiver.xml'
    ],   
    'installable': True,
    'application': True,
}
