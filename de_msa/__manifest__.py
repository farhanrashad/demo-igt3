# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Master Service Agreement",
    "category": 'Agreement',
    "summary": "Master Service Agreement",
    "description": """
	 
   
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '14.1.0.0',
    "depends": ['product','project'],
    "data": [
        'security/ir.model.access.csv',
        'views/master_service_agreement_view.xml',
        'views/sla_factor_views.xml',
        'views/wind_factor_views.xml',
        'views/product_view.xml',
        'views/msa_menu.xml',
#         'report/employee_report_pdf.xml',
    ],
    
    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
