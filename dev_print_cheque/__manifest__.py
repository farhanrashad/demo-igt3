# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<https://www.dynexcel.com>).
#
#    For Module Support : info@gdynexcel.com  or Skype : Dynexcel 
#
##############################################################################

{
    'name': 'Dynamic Print Cheque - Check writing',
    'version': '14.0.0.2',
    'sequence':1,
    'category': 'Generic Modules/Accounting',
    'description': """
         odoo App will  configure and print cheque/check Dynamically for any bank with different Cheque format.

Cheque print, check print, check writing, bank check print, check dynamic, bank cheque, cheque dynamic, cheque printing, bank cheque, dynamic print cheque, cheque payment, payment check, 

    Dynamic print cheque
    How can we create dynamic cheque
    Dynamic cheque print
    Accounting voucher
    Cheque acconting voucher
    Odoo dynamic cheque
    Odoo dynamic cheque print
    Print dynamic cheque
    Odoo11 dynamic cheque print
    Print cheque
    Print cheque odoo
    Dynamically print cheque
    Dynamic cheque
    Cheque accounting voucher
    Accounting cheque voucher
    Dynamic bank cheque
    Dynamic bank cheque print in odoo
    Odoo dynamic cheque
    Odoo dynamic bank cheque
    Odoo dynamic bank cheque print
    cheque Printer
    check print
    dynamic check print
    check printing configuration
    cheque printing
    payment cheque print
    cheque payment print 


    """,
    'author': 'Dynexcel',
    'summary':'App will  configure and print cheque/check Dynamically for any bank with different Cheque format',
    'website': 'https://www.dynexcel.com/',
    'depends': ['account_accountant','account_payment','account_check_printing'],
    'data': [
        'security/ir.model.access.csv',
        'views/report_print_cheque.xml',
        'views/report_menu.xml',
        'views/cheque_setting_view.xml',
        'views/account_vocher_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':45.0,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/usddBBEk1Tg',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
