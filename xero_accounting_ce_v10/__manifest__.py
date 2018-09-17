{
    'name': 'Xero Odoo Integration App',
    'version': '1.1',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'category': 'Accounting',
    'website': 'www.pragtech.co.in',
    'description': """
Integration with Xero Accounting new API.
===============================
-Export Partners,Products,Invoices from OpenERP to Xero
--------------------------------------------------------
-Import Payments from Xero
--------------------------
""",
    'depends': ['base', 'portal', 'stock', 'l10n_in_stock', 'account', 'account_voucher', 'product', 'purchase', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'wizard/invoice_import_export_view.xml',
        'wizard/import_payments_view.xml',
        'wizard/purchase_import_export_view.xml',
        'wizard/validate_wizard_view.xml',
        'wizard/success_msg_view.xml',
        'view/purchase_view.xml',
        'view/res_company_view.xml',
        'view/xero_import_export_view.xml',
        'view/menu_view.xml',
        'view/account_invoice_view.xml',
        'view/xero_logs_view.xml',
        'view/sale_view.xml',
        'view/partner_view.xml',
    ],
    'price': 300,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': ['static/description/odooxero_v11.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
