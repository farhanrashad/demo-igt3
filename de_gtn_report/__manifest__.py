# -*- coding: utf-8 -*-

{
    "name": "Gtn Report Print",
    'version': '14.0.0.0',
    "category": 'GTN REPORT PRINT FOR INVENTORY STOCK MODULE',
    "summary": ' Iventory variations',
    'sequence': 7,
    "description": """"  """,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    'license': 'LGPL-3',
    'depends': ['base','stock'],
    'data': [


        'report/gtn_report.xml',
        'views/transfer_tab.xml',

    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}

