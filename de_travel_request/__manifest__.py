# -*- coding: utf-8 -*-
{
    'name': "Travel Request",
    'summary': """Travel Request""",
    'description': """ """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Hr',
    'version': '14.0.0.2',
    'depends': ['base', 'hr','digest'],
    'data': [
        'security/ir.model.access.csv',
        'data/form_name.xml',
        'views/travel_request_view.xml',
        'views/travel_request_menu.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
