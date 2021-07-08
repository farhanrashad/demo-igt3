# -*- coding: utf-8 -*-

{
    'name': 'EMPFIN Employee Advances',
    'version': '14.0.1.2',
    'summary': 'Employee Advance Request',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Human Resources',
    'author': "Dynexcel",
    'company': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'website': "https://www.dynexcel.com",
    'depends': [
        'hr_payroll', 'de_empfin_core', 'account_accountant',  'hr_expense'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/salary_advance_data.xml',
        'views/product_views.xml',
        'views/salary_structure_views.xml',
        'views/salary_advance_views.xml',
        'views/hr_advance_type_views.xml',
        'views/hr_expense_views.xml',
    ],
    
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

