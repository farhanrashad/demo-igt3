# -*- coding: utf-8 -*-
{
    'name': "Penalty Journal Entry",

    'summary': """
        Customize Penalty Entry Bills
        """,

    'description': """
        Customize Penalty Entry
        Depends on Purchase Subscription
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Accounting',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['de_operations','account'],

    # always loaded
    'data': [
        'security/account_security.xml',
        'wizard/penalty_entry_refuse_wizard.xml',
        'security/ir.model.access.csv',
        'views/penalty_entry_menu.xml',
        'views/penalty_entry_type_views.xml',
        'views/penalty_entry_stage_views.xml',
        'views/account_move_views.xml',
        'views/penalty_entry_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
