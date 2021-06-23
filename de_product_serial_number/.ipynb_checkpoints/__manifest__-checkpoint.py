# -*- coding: utf-8 -*-
{
    'name': "Product Serial Number",

    'summary': """
        Product Serial Number
        """,

    'description': """
        Product Bulk Serial Number
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_serial_generate_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
