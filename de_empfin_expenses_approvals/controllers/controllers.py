# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpfinExpensesApprovals(http.Controller):
#     @http.route('/de_empfin_expenses_approvals/de_empfin_expenses_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_empfin_expenses_approvals/de_empfin_expenses_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_empfin_expenses_approvals.listing', {
#             'root': '/de_empfin_expenses_approvals/de_empfin_expenses_approvals',
#             'objects': http.request.env['de_empfin_expenses_approvals.de_empfin_expenses_approvals'].search([]),
#         })

#     @http.route('/de_empfin_expenses_approvals/de_empfin_expenses_approvals/objects/<model("de_empfin_expenses_approvals.de_empfin_expenses_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_empfin_expenses_approvals.object', {
#             'object': obj
#         })
