# -*- coding: utf-8 -*-
{
    'name': "Top Up",
    'summary': """Employee Training App Modification""",
    'description': """ """,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Uncategorized',
    'version': '14',
    'depends': ['base', 'hr','digest','base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/request_view.xml',
        'views/hr_employee_views.xml',
        'data/form_name.xml',
        'views/balance_views.xml',
        'views/top_up_menu.xml',
        'views/reporting_balance.xml',
        'views/reporting_request.xml',

    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
