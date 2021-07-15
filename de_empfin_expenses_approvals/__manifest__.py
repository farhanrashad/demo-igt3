# -*- coding: utf-8 -*-
{
    'name': "Expenses Approvals",

    'summary': """
        Expenses Approvals
        """,

    'description': """
        Expenses Approvals
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Expenses',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense','de_empfin_advances'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
