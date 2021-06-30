# -*- coding: utf-8 -*-
{
    'name': "Requisition Workflow",

    'summary': """
        Requisition Workflow
        """,

    'description': """
        Requisition Workflow
        - Stages Workflow
        - Security Groups
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Purchase',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_requisition'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/requisition_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
