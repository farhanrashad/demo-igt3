# -*- coding: utf-8 -*-
{
    'name': "Employee Assets",

    'summary': """
        This module adds an assets page on employee form""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/employee_asset_view.xml',
        'views/employee_asset_view_inh.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
