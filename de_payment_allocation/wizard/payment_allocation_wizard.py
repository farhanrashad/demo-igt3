# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class PaymentAllocation(models.Model):
    _name = 'payment.allocation.wizard'
    _description = 'Payment Allocation Wizard'
    
    
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    is_payment = fields.Boolean(string='Is Payment')
    is_invoice = fields.Boolean(string='Is Invoice')
    account_id = fields.Many2one('account.account', string='Account', required=False)
    amount = fields.Float(string='Amount')
    payment_line_ids = fields.One2many('payment.allocation.wizard.line', 'allocation_id', string='Payment Lines')
    invoice_line_ids = fields.One2many('invoice.allocation.wizard.line', 'allocation_id', string='Invoice Lines')
    payment_id = fields.Many2one('account.payment', string='Payment')
    move_id = fields.Many2one('account.move', string='Move')
    journal_id = fields.Many2one(related='payment_id.journal_id')
    payment_type = fields.Selection(related='payment_id.payment_type')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method',
        readonly=False, store=True,
        compute='_compute_payment_method_id',
        
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    
    
    @api.depends('journal_id')
    def _compute_payment_method_id(self):
        for wizard in self:
            payment_type = wizard.payment_type

            if payment_type == 'inbound':
                available_payment_methods = wizard.journal_id.inbound_payment_method_ids
            else:
                available_payment_methods = wizard.journal_id.outbound_payment_method_ids

            # Select the first available one by default.
            if available_payment_methods:
                wizard.payment_method_id = available_payment_methods[0]._origin
            else:
                wizard.payment_method_id = False
                
                
    def action_allocate_invoice_payment(self):
        tot_payment_amount = 0.0
        tot_invoice_amount = 0.0  
        for invoice in self.invoice_line_ids:
            if invoice.allocate == True:
                tot_invoice_amount = tot_invoice_amount + invoice.allocate_amount  
                
        for payment_line in self.payment_line_ids: 
            if payment_line.allocate == True:
                if payment_line.payment_id.currency_id.id == self.move_id.currency_id.id:
                    tot_payment_amount = tot_payment_amount + payment_line.allocate_amount
                else:
                    tot_payment_amount = tot_payment_amount + payment_line.payment_id.currency_id._convert(payment_line.allocate_amount, self.move_id.currency_id, self.move_id.company_id, self.move_id.date)

        if tot_payment_amount > tot_invoice_amount :
            raise UserError(_('You Are Not Allowed To Enter Amount greater than '+str(tot_invoice_amount)))
       
        for payment in self.payment_line_ids:
            if payment.allocate == True:
                debit_line = 0
                credit_line = 0
                payment_debit_line = 0
                for line in self.move_id.line_ids:
                    if line.credit != 0.0:
                        credit_line = line.id 
                    if line.credit == 0.0:
                        debit_line = line.id  
                        
                for payment_line in payment.payment_id.move_id.line_ids:                    
                    payment_debit_line = payment_line.id
                recocile_vals = {
                    'exchange_move_id': self.move_id.id,
                }
                reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
                amount_reconcile = 0.0
                if payment.payment_id.currency_id.id == self.move_id.currency_id.id:
                    amount_reconcile = payment.allocate_amount
                else:
                    amount_reconcile = payment.payment_id.currency_id._convert(payment.allocate_amount, self.move_id.currency_id, self.move_id.company_id, self.move_id.date)    
                vals = {
                    'full_reconcile_id': reconcile_id.id,
                    'amount':  payment.allocate_amount,
                    'credit_move_id':  credit_line,
                    'debit_move_id': payment_debit_line,
                    'credit_amount_currency': amount_reconcile,
                    'debit_amount_currency': amount_reconcile,
                }
                partial_payment = self.env['account.partial.reconcile'].create(vals)
                
        
                
    
    
    def action_allocate_payment(self):
        invoice_line = []
        line_ids = []
        if self.payment_id.amount == self.payment_id.reconcile_amount:
            raise UserError(_('This Payment Already reconciled'))  
        tot_invoice_amount = 0.0  
        tot_payment_amount = 0.0    
        for invoice in self.invoice_line_ids:
            if invoice.allocate == True:
                tot_invoice_amount = tot_invoice_amount + invoice.allocate_amount  

        for payment_line in self.payment_line_ids:                    
            tot_payment_amount = tot_payment_amount + payment_line.allocate_amount
        if tot_invoice_amount  > tot_payment_amount:
            raise UserError(_('You Are Not Allowed To Enter Amount greater than '+str(tot_payment_amount)))     
        for invoice in self.invoice_line_ids:
            if invoice.allocate == True:
                invoice_line.append(invoice.move_id.invoice_line_ids.ids)
                line_ids.append(invoice.move_id.line_ids.ids)
                debit_line = 0
                credit_line = 0
                payment_debit_line = 0
                for line in invoice.move_id.line_ids:
                    if line.credit != 0.0:
                        credit_line = line.id 
                    if line.credit == 0.0:
                        debit_line = line.id    
                invoice.move_id.id
                for payment_line in self.payment_id.move_id.line_ids:                    
                    payment_debit_line = payment_line.id
                recocile_vals = {
                    'exchange_move_id': invoice.move_id.id,
                }
                reconcile_id = self.env['account.full.reconcile'].create(recocile_vals)
                 
                
                amount_reconcile = 0.0
                if invoice.move_id.currency_id.id == self.payment_id.currency_id.id:
                    amount_reconcile = invoice.allocate_amount
                else:
                    amount_reconcile = self.payment_id.currency_id._convert(invoice.allocate_amount, invoice.move_id.currency_id, invoice.move_id.company_id, invoice.move_id.date) 
                vals = {
                    'full_reconcile_id': reconcile_id.id,
                    'amount':  invoice.allocate_amount,
                    'credit_move_id':  credit_line,
                    'debit_move_id': payment_debit_line,
                    'credit_amount_currency': amount_reconcile,
                    'debit_amount_currency': amount_reconcile,
                }
                payment = self.env['account.partial.reconcile'].create(vals)
                
                
    
class PaymentAllocationLine(models.Model):
    _name = 'payment.allocation.wizard.line'
    _description = 'Payment Allocation Wizard Line'
    
    
    payment_id = fields.Many2one('account.payment', string='Payment')
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation')
    payment_amount = fields.Float(string='Payment Amount')
    payment_date = fields.Date(string='Payment Date')
    unallocate_amount = fields.Float(string='Unallocated Amount')
    allocate = fields.Boolean(string='Allocate')
    allocate_amount = fields.Float(string='allocate Amount')
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    original_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Payment Currency')
    
    
    
    @api.onchange('allocate')
    def onchange_allocate(self):
        invoice_amount = 0.0
        payment_amount = 0.0
        amount = 0.0
        invoice_amount = self.allocation_id.move_id.amount_residual     
        for inv in self:
            if inv.allocate == True:
                if inv.payment_id.currency_id.id == self.allocation_id.move_id.id:                              
                    payment_amount = payment_amount + inv.allocate_amount   
                else:
                    payment_amount = payment_amount +  inv.payment_id.currency_id._convert(inv.allocate_amount, inv.allocation_id.move_id.currency_id, inv.allocation_id.move_id.company_id, inv.allocation_id.move_id.date)

        if  invoice_amount <  payment_amount:
            amount = payment_amount - invoice_amount
            raise UserError(_('Allocate Amount cannot be greater than '+str(payment_amount)))

    
    
class InvoiceAllocationLine(models.Model):
    _name = 'invoice.allocation.wizard.line'
    _description = 'Invoice Allocation Wizard Line'
    
    
    move_id = fields.Many2one('account.move', string='Invoice')
    allocation_id = fields.Many2one('payment.allocation.wizard', string='Allocation')
    payment_date = fields.Date(string='Invoice Date')
    due_date = fields.Date(string='Due Date')
    invoice_amount = fields.Float(string='Invoice Amount')
    unallocate_amount = fields.Float(string='Unallocated Amount')
    allocate = fields.Boolean(string='Allocate')
    allocate_amount = fields.Float(string='allocate Amount')
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Currency')
    original_currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=False,
        string='Invoice Currency')
    
    
    @api.onchange('allocate')
    def onchange_allocate(self):
        payment_amount = 0.0
        inv_amount = 0.0
        amount = 0.0
        for payment in self.allocation_id.payment_line_ids:
            payment_amount = payment.allocate_amount     
        for inv in self:
            if inv.allocate == True:
                if inv.move_id.currency_id.id == inv.allocation_id.payment_id.currency_id.id:                
                    inv_amount = inv_amount + inv.allocate_amount
                else:
                    inv_amount = inv_amount + inv.move_id.currency_id._convert(inv.allocate_amount, inv.allocation_id.payment_id.currency_id, inv.allocation_id.payment_id.company_id, inv.allocation_id.payment_id.date)


        if  payment_amount <  inv_amount:
            amount = inv_amount - payment_amount
            raise UserError(_('Allocate Amount cannot be greater than '+str(payment_amount)))

            
            