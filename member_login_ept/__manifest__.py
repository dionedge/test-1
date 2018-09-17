# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Member Login Ept',
    'version' : '1.1',
    'summary': 'Manage customer attendances',
    'sequence': 30,
    'description': """
         This module aims to manage customer's attendances.
    """,
    'category': '',
    'website': 'https://www.emiprotechnologies.com',
    'depends' : ['base','hr','menu_setting_ept'],
    'data': [
            'views/member_login_ept.xml',
            'views/web_asset_backend_template_ept.xml', #Added by KM
            'views/hr_employee_view_ept.xml',
            'views/timesheet_ept.xml',
            'views/classes_ept.xml',
            'views/class_scheduler.xml',
            'security/member_login.xml' ,            
            'security/ir.model.access.csv',
            'data/attendance_cron.xml',
            'report/class_attendance_report.xml',
            'report/instructors_attandance_report.xml',
            'views/hr_attendance.xml',
            'report/member_attendance_analysis_report.xml',
            'views/res_config_settings.xml',

            'views/res_partner_ept.xml'
     ],
    
    'qweb': [
        "static/src/xml/attendance_ept.xml"
    ],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
