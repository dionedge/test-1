# -*- coding: utf-8 -*-
{
    'name': "Timesheets/Attendances Reporting Ept",
    'version': '11.0',
    'category': 'Human Resources',
    'sequence': 100,
    'summary': 'Timesheets, Attendances',
    'description': """
    Module linking the timesheet and its attendance ..
    """,
        
    'website': 'https://www.emiprotechnologies.com',
    'author' : 'Emipro Technologies Pvt Ltd',
    
    'depends': ['hr_timesheet_sheet', 'hr_attendance'],
        'data': [
        'security/ir.model.access.csv',
        'report/hr_timesheet_attendance_report_view.xml',
        'views/hr_timesheet_sheet_views.xml',
        #'views/hr_timesheet_attendance_config_settings_views.xml',
    ],
    
    'auto_install': True,
}
