# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import date

class HRExpenseSheetStage(models.Model):
    _name = 'hr.expense.sheet.stage'
    _description = 'Expense Stage'
    _order = 'sequence, stage_category, id'

    def _get_default_expense_sheet_type_ids(self):
        default_expense_sheet_type_id = self.env.context.get('default_expense_sheet_type_id')
        return [default_expense_sheet_type_id] if default_expense_sheet_type_id else None
    
    name = fields.Char(string='Stage Name', required=True, translate=True)
    stage_code = fields.Char(string='Code', size=3, copy=False)
    description = fields.Text(
        "Requirements", help="Enter here the internal requirements for this stage. It will appear "
                             "as a tooltip over the stage's name.", translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    expense_sheet_type_ids = fields.Many2many('hr.expense.sheet.type', 'expense_sheet_type_stage_rel', 'expense_sheet_stage_id', 'expense_sheet_type_id', string='Expense Types',
        default=_get_default_expense_sheet_type_ids)
    
    stage_category = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('confirm', 'Confirmed'),
        ('closed', 'Closed'),
    ], string='Category', default='draft')
    
    next_stage_id = fields.Many2one('account.custom.entry.stage', string='Next Stage' )
    prv_stage_id = fields.Many2one('account.custom.entry.stage', string='Previous Stage')

    group_id = fields.Many2one('res.groups', string='Security Group')
    
    _sql_constraints = [
        ('code_uniq', 'unique (stage_code)', "Code already exists!"),
    ]

class HRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        expense_sheet_type_id = self.env.context.get('default_expense_sheet_type_id')
        if not expense_sheet_type_id:
            return False
        return self.stage_find(expense_sheet_type_id, [('fold', '=', False)])
    
    stage_id = fields.Many2one('hr.expense.stage', string='Stage', compute='_compute_stage_id', store=True, readonly=False, ondelete='restrict', tracking=True, index=True, default=_get_default_stage_id, domain="[('expense_sheet_type_ids', '=', expense_sheet_type_id)]", copy=False)
    
    @api.depends('hr_expense_sheet_type_id')
    def _compute_stage_id(self):
        for expense in self:
            if expense.hr_expense_sheet_type_id:
                if expense.custom_entry_type_id not in expense.stage_id.expense_sheet_type_ids:
                    expense.stage_id = expense.stage_find(expense.hr_expense_sheet_type_id.id, [
                        ('fold', '=', False)])
            else:
                expense.stage_id = False
    
    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('hr_expense_sheet_type_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('expense_sheet_type_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['hr.expense.sheet.stage'].search(search_domain, order=order, limit=1).id
