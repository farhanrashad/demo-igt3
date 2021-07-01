# -*- coding: utf-8 -*-
{
    'name': "Employee PIT",
    'summary': """Employee PIT""",
    'description': """ """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Payroll',
    'version': '14.0.0.2',
    'depends': ['base', 'hr','hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/employee_pit_data.xml',
        'views/employee_pit.xml',
        'views/employee_pit_menu.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
