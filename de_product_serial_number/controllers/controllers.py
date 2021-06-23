# -*- coding: utf-8 -*-
# from odoo import http


# class DeProdutSerialNumber(http.Controller):
#     @http.route('/de_produt_serial_number/de_produt_serial_number/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_produt_serial_number/de_produt_serial_number/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_produt_serial_number.listing', {
#             'root': '/de_produt_serial_number/de_produt_serial_number',
#             'objects': http.request.env['de_produt_serial_number.de_produt_serial_number'].search([]),
#         })

#     @http.route('/de_produt_serial_number/de_produt_serial_number/objects/<model("de_produt_serial_number.de_produt_serial_number"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_produt_serial_number.object', {
#             'object': obj
#         })
