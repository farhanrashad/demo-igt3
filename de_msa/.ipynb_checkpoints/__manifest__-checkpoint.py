# -*- coding: utf-8 -*-
{
    'name': "Master Service Agreement",

    'summary': """
        Master Service Agreement
        Telecom Billing
        """,

    'description': """
        Master Service Agreement
        - Telecom Billing
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Sale',
    'version': '14.0.0.4',

    'depends': ['base','product','project','account','contacts'],

    'data': [
        'security/msa_security.xml',
        'security/ir.model.access.csv',
        'views/master_service_agreement_view.xml',
        'views/billing_info_view.xml',
        'views/monthly_models_view.xml',
        'views/sla_factor_views.xml',
        'views/wind_factor_views.xml',
        'views/product_view.xml',
        'views/project_project_view.xml',
        'views/account_move_view.xml',
        'views/msa_menu.xml',
#         'report/employee_report_pdf.xml',
    ],
    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
