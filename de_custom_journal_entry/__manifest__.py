# -*- coding: utf-8 -*-
{
    'name': "Third-Party Billing",
    'summary': """
        Customize Journal Entries
        """,
    'description': """
        Customize Journal Entry
        
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Accounting',
    'version': '14.0.0.7',
    
    'depends': ['de_purchase_subscription','account', 'fleet', 'project','stock','purchase_requisition','purchase','de_travel_request'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/custom_entry_menu.xml',
        'views/custom_entry_type_views.xml',
        'views/custom_entry_stage_views.xml',
        'views/account_move_views.xml',
        'views/custom_entry_views.xml',
        'views/account_payment_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
