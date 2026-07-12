# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TransitopsDriver(models.Model):
    _name = 'transitops.driver'
    _description = 'Driver'
    _order = 'name asc'

    name = fields.Char(string='Driver Name', required=True)
    license_number = fields.Char(string='License Number', required=True)
    license_expiry_date = fields.Date(string='License Expiry Date', required=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
    ], string='Status', default='available', required=True)
