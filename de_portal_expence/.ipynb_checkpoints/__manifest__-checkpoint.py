# -*- coding: utf-8 -*-
{
    'name': "Portal Expense",

    'summary': """
        Employee  Expense Record From Portal""",

    'description': """
        Employee  Expense Record From Portal
        1- Submit Expense Record From Portal
        2- View Expense Record From Portal
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense', 'hr','web','de_hr_portal_user','de_expense_enhancement'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_expense_views.xml',
        'views/portal_expense_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
