# -*- coding: utf-8 -*-
{
    'name': "Import Material Requisition",

    'summary': """
        Import Material Requisition  from task
        """,

    'description': """
        Import Material Requisition  from task
    """,

    'author': "Dynexecel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'de_stock_material_transfer'],

    # always loaded
    'data': [
        'data/ir_server_action.xml',
        'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/project_task_template.xml',
        'views/stock_transfer_category_views.xml',
        'views/stock_tansfer_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
