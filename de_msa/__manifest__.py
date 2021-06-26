# -*- coding: utf-8 -*-
{
    'name': "Master Service Agreement",

    'summary': """
        Master Service Agreement
        """,

    'description': """
        Master Service Agreement
    """,

    'author': "Dynexccel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Agreement',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','project','account'],

    # always loaded
    'data': [
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
