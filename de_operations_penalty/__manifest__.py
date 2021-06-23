# -*- coding: utf-8 -*-
{
    'name': "Operations Penalties",

    'summary': """
        Operations Penalties
        """,

    'description': """
        Operations Penalties:-
        1. SLA Penalty
        2. PM Penalty
        3. Materail Penalty
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Accounting',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['de_operations','account'],

    # always loaded
    'data': [
        'security/penalty_security.xml',
        #'wizard/penalty_entry_refuse_wizard.xml',
        'security/ir.model.access.csv',
        'views/penalty_menu.xml',
        'views/penalty_type_views.xml',
        'views/penalty_stage_views.xml',
        'views/penalty_config_views.xml',
        'views/account_move_views.xml',
        'views/penalty_entry_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
