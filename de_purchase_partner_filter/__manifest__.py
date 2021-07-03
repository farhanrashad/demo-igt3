# -*- coding: utf-8 -*-
{
    'name': "Partner Filter",

    'summary': """
    Purchase Partner Filter
        """,

    'description': """
        Purchase Partner Filter
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Purchase',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
