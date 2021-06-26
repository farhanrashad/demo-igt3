# -*- coding: utf-8 -*-
{
    'name': "MSA Report Report",

    'summary': """
        MSA Report Report
        """,

    'description': """
       MSA Report Report
    """,

    'author': "Dynexccel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Agreement',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'de_msa'],

    # always loaded
    'data': [
        'views/view_msa_report.xml',
        'reports/msa_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

