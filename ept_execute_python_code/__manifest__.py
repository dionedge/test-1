{
    "name": "Execute Python Code",
    "description": """
Installing this module, user will able to execute python code from OpenERP
""",
    "author": "OpenERP SA",
    "version": "0.1",
    "depends": ["base"],
    "init_xml": [],
    "data": [
        'view/python_code_view.xml',
        'view/cron_code_execute.xml',
    ],
    "demo_xml": [],
    "installable": True,
}
