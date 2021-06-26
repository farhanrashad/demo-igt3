# -*- coding: utf-8 -*-
{
    'name': "MSA Report Report",
    'summary': """Generate MSA Excel Report""",
    'description': """Generate MSA Report""",
    'author': "Dynexcel",
    'website': "https://www.dynexcel.co",
    'sequence': 1,
    'category': 'MSA',
    'version': '14.0.0.1',
    'depends': ['base', 'de_msa'],
    'data': [
        'views/view_msa_report.xml',
        'reports/msa_report.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
