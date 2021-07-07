# -*- coding: utf-8 -*-
{
    'name': "Employee Overtime",

    'summary': """
        Overtime Menu in Attendance app after  checkin/checkout
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel123.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_attendance','hr_payroll','de_shift_attendance'],

    # always loaded
    'data': [
        'wizard/overtime_wizard.xml',
        'data/schedular_action.xml',
        'security/ir.model.access.csv',
        'views/overtime_views.xml',
        'views/overtime_rule_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
