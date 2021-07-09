# -*- coding: utf-8 -*-
{
    'name': "Employee Overtime",

    'summary': """
        Manage Employee Overtime""",

    'description': """
        Helps you to manage Employee Overtime.
    """,

    'author': "Dynexcel",
    'website': "httsp://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.0.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_contract', 'hr_holidays','hr_payroll', 'hr_attendance','project','hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/overtime_menu.xml',
        #'views/res_config_settings_views.xml',
        'views/overtime_type_views.xml',
        'views/hr_contract_views.xml',
        'views/overtime_request_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
       'data/hr_overtime_demo.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
