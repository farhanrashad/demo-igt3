# -*- coding: utf-8 -*-
{
    'name': "PO Deviation Report",
    'summary': """Generate PO Deviation Report""",
    'description': """
        Generate PO Deviation Report
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.co",
    'sequence':1,
    'category': 'Agreement',
    'version': '14.0.0.2',
    'depends': ['base','stock','purchase','sale'],
    'data': [
        'security/ir.model.access.csv',
        #'views/view_purchase_order.xml',
        'reports/po_deviation_report.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
