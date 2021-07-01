# -*- coding: utf-8 -*-

{
    "name": "Requisition Lines Report",
    'version': '14.0.0.0',
    "category": 'Requisition Lines Report',
    "summary": ' Requisition Lines Report',
    'sequence': 1,
    "description": """"Generate Requisition Lines Report """,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'depends': ['base','stock','purchase','hr','de_stock_material_transfer'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/gtn_dgn_mrf_spmrf_wizard.xml',
        'views/view_stock_transfer_order.xml',
        'reports/mrf_spmrf_report.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

