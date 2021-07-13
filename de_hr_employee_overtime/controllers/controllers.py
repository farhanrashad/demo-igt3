# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeesOvertime(http.Controller):
#     @http.route('/de_employees_overtime/de_employees_overtime/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employees_overtime/de_employees_overtime/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employees_overtime.listing', {
#             'root': '/de_employees_overtime/de_employees_overtime',
#             'objects': http.request.env['de_employees_overtime.de_employees_overtime'].search([]),
#         })

#     @http.route('/de_employees_overtime/de_employees_overtime/objects/<model("de_employees_overtime.de_employees_overtime"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employees_overtime.object', {
#             'object': obj
#         })
