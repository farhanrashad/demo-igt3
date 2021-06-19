# -*- coding: utf-8 -*-
{
    'name': "Training",

    'summary': """
        Employee Training
        1-provide employee training through sessions
        """,

    'description': """
Employee Training
        1-provide employee training through sessions""",

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Employee',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','mail'],

    # always loaded
    'data': [
        'data/sessions_seq.xml',
        'data/course_seq.xml',
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'views/sessions_views.xml',
        'views/course_views.xml',
        'views/configuration_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
