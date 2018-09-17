{
    'name': 'Adaptiv Backend Theme',
    'version': '11.0.0.107',
    'category': 'Themes/Backend',
    'summary': "Enhance your Odoo experience with this completely rewritten backend theme for Odoo 11.",
	'description': "",
    'author': 'Adaptiv Design',
    'license': 'OPL-1',
    'price': 149.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'url': 'http://demo.adaptiv.nl',
    'live_test_url': 'http://demo.adaptiv.nl',
    'depends': [
        'web',
        'web_diagram'
    ],
    'data': [
        'views/webclient_templates.xml',
        'views/res_company_view.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/main.png',
        'static/description/main_screenshot.png'
    ]
}
