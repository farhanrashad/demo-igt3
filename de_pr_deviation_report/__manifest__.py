# -*- coding: utf-8 -*-
{
    'name': "PR Deviation Report",
    'summary': """Generate PR Deviation Report""",
    'description': """
        Generate PR Deviation Report
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.co",
    'sequence':1,
    'category': 'Agreement',
    'version': '14.0.0.3',
    'depends': ['base','stock','purchase','sale'],
    'data': [
        # 'security/ir.model.access.csv',
        #'views/view_purchase_order.xml',
        'reports/pr_deviation_report.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
