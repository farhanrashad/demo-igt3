# -*- coding: utf-8 -*-
{
    'name': "PO Line Report",
    'summary': """Generate PO Line Excel Report""",
    'description': """
        Generate PO Line Report
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.co",
    'sequence':1,
    'category': 'Agreement',
    'version': '14.0.0.2',
    'depends': ['base','stock','purchase','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/view_purchase_order.xml',
        'reports/po_line_report.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
