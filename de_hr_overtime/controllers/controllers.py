# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrOvertime(http.Controller):
#     @http.route('/de_hr_overtime/de_hr_overtime/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_overtime/de_hr_overtime/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_overtime.listing', {
#             'root': '/de_hr_overtime/de_hr_overtime',
#             'objects': http.request.env['de_hr_overtime.de_hr_overtime'].search([]),
#         })

#     @http.route('/de_hr_overtime/de_hr_overtime/objects/<model("de_hr_overtime.de_hr_overtime"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_overtime.object', {
#             'object': obj
#         })
