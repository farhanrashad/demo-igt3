# -*- coding: utf-8 -*-
{
    'name': "Employee PIT",
    'summary': """Employee PIT""",
    'description': """ """,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Uncategorized',
    'version': '14.0.0.2',
    'depends': ['base','hr', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/form_name.xml',
        'views/employee_pit.xml',
        'views/employee_pit_menu.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
