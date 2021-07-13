from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GradeDesignation(models.Model):
    _inherit = 'grade.designation'

    grade_line_ids = fields.One2many('grade.designation.line',
                                     'grade_designation_id')  # fields to Connect main and child Models


class GradeDesignationLine(models.Model):
    _name = 'grade.designation.line'
    _description = 'Grade Desgnation Line Model'

    grade_designation_id = fields.Many2one('grade.designation')  # fields to connect line model to Main Model
    expense_type = fields.Many2one('product.product', required=True)
    limit = fields.Integer(string='Limit', required=True)
    period = fields.Selection([('1', '1 Year'), ('2', '2 Year'), ('3', '3 Year'), ('4', '4 Year')]
                              , string='Period', required=True)
    funds_request_limit = fields.Integer('Funds Request Limit')
    funds_request_period = fields.Selection([('1', '1 Year'), ('2', '2 Year'), ('3', '3 Year'), ('4', '4 Year')]
                                            , string='Funds Request Period')

    @api.model
    def create(self, vals):
        product_id = vals['expense_type']
        product = self.env['product.product'].search([('id', '=', product_id)])
        if product.can_be_expensed == True and product.is_petty_cash == True:
            raise UserError(('You are not allowed to Select this Product ' + str(product.name)))
        result = super(GradeDesignationLine, self).create(vals)
        return result

    @api.model
    def write(self, vals):
        rec = super(GradeDesignationLine, self).write(vals)
        product_id = vals['expense_type']
        product = self.env['product.product'].search([('id', '=', product_id)])
        if product.can_be_expensed == True and product.is_petty_cash == True:
            raise UserError(('You are not allowed to Select this Product ' + str(product.name)))
        return rec

    @api.onchange('expense_type')
    def _onchange_exp(self):
        ids = []
        product_ids = self.env['product.product'].search(
            [('can_be_expensed', '=', True), ('is_petty_cash', '=', False)])
        if product_ids:
            for product in product_ids:
                ids.append(product.id)
        return {'domain': {'expense_type': [('id', '=', ids)]}}



    @api.constrains('expense_type')
    def _onchange_expense_type(self):
        list = []
        for rec in self.grade_designation_id.grade_line_ids:
            list.append(rec.expense_type.id)
        for id in list:
            count = list.count(id)
            if count > 1:
                raise UserError("Sorry! You cannot select same Product multiple times!")
