# -*- coding: utf-8 -*-
{
    'name': 'Sale Subscription Ept',
    'version': '1.0', 
    'author':'Emipro Technologies',
    'category': 'Website',
    'website': ' www.emiprotechnologies.com',
    'description': "",
    'depends': ['website_sale','sale_subscription'],
    'data': [
          'security/ir.model.access.csv',
          'views/kaijin_agreement.xml',
          'templates/template.xml',
          'templates/asset.xml',
          'data/sale_subscription_cron.xml',
    ],  
    'qweb': [
        'static/src/xml/signature.xml',
    ],  
    'installable': True,
    'application': True,
}
