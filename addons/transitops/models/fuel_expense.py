# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TransitopsFuelLog(models.Model):
    _name = 'transitops.fuel.log'
    _description = 'Fuel Log'
    _order = 'date desc'

    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True)
    liters = fields.Float(string='Fuel Liters', required=True)
    cost = fields.Float(string='Total Cost ($)', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)

    @api.constrains('liters', 'cost')
    def _check_values(self):
        for log in self:
            if log.liters <= 0.0 or log.cost <= 0.0:
                raise ValidationError(_("Fuel liters and cost must be greater than zero!"))

class TransitopsExpense(models.Model):
    _name = 'transitops.expense'
    _description = 'General Expense'
    _order = 'date desc'

    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True)
    expense_type = fields.Selection([
        ('tolls', 'Tolls'),
        ('insurance', 'Insurance'),
        ('taxes', 'Taxes'),
        ('other', 'Other'),
    ], string='Expense Type', required=True, default='tolls')
    description = fields.Char(string='Description')
    cost = fields.Float(string='Cost ($)', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)

    @api.constrains('cost')
    def _check_cost(self):
        for expense in self:
            if expense.cost <= 0.0:
                raise ValidationError(_("Expense cost must be greater than zero!"))
