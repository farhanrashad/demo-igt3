# -*- coding: utf-8 -*-
{
    'name': "Shift Attendance",

    'summary': """
        Employee Shift  Attendance""",

    'description': """
         Employee Shift  Attendance Type below
         1- Morning
         2- Evening
         3- Night
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Attendance',
    'version': '14.0.0.1',

    'depends': ['base','hr_attendance'],

    'data': [
        'wizard/shift_allocation_wizard.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/hr_attendance_views.xml', 
        'views/shift_attendance_view.xml',
        'views/shift_allocation_view.xml',
        'views/shift_management_view.xml',
    ],

}
