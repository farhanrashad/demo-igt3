# -*- coding: utf-8 -*-
{
    'name': "Custom Entry Approvals",

    'summary': """
        Custom Entry Approvals
        """,

    'description': """
        Custom Entry Approvals 
        1- Multi Level Approvals
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'Purchase/Subscription',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','de_multi_level_approvals','de_custom_journal_entry'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/custom_entry_type_views.xml',
        'views/approval_approver_views.xml',
        'views/approval_request_views.xml',
        'views/custom_entry_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
