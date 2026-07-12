# -*- coding: utf-8 -*-
from odoo import models, fields, api, _  # type: ignore[import]
from odoo.exceptions import ValidationError  # type: ignore[import]
from datetime import date

class TransitopsDriver(models.Model):
    _name = 'transitops.driver'
    _description = 'Driver Profile'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    license_number = fields.Char(string='License Number', required=True)
    license_category = fields.Selection([
        ('class_a', 'Class A (Heavy Commercial)'),
        ('class_b', 'Class B (Medium Commercial)'),
        ('class_c', 'Class C (Light Commercial)'),
        ('class_d', 'Class D (Standard Passenger)'),
    ], string='License Category', required=True, default='class_d')
    license_expiry_date = fields.Date(string='License Expiry Date', required=True)
    contact_number = fields.Char(string='Contact Number')
    safety_score = fields.Float(string='Safety Score (0-100)', default=100.0)
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('off_duty', 'Off Duty'),
        ('suspended', 'Suspended'),
    ], string='Status', default='available', required=True, tracking=True)
    active = fields.Boolean(default=True)

    is_license_expired = fields.Boolean(string='License Expired', compute='_compute_license_expired', store=True)

    trip_ids = fields.One2many('transitops.trip', 'driver_id', string='Trips')

    _sql_constraints = [
        ('unique_license_number', 'unique(license_number)', 'The driver license number must be unique!'),
    ]

    @api.depends('license_expiry_date')
    def _compute_license_expired(self):
        today = date.today()
        for driver in self:
            if driver.license_expiry_date:
                driver.is_license_expired = driver.license_expiry_date < today
            else:
                driver.is_license_expired = False

    @api.constrains('safety_score')
    def _check_safety_score(self):
        for driver in self:
            if driver.safety_score < 0.0 or driver.safety_score > 100.0:
                raise ValidationError(_("Safety score must be between 0 and 100!"))
            if driver.safety_score < 50.0 and driver.status == 'available':
                # Automatically suspend or warn driver if safety score is too low
                # mark as suspended
                driver.status = 'suspended'

    @api.constrains('license_expiry_date')
    def _check_license_expiry(self):
        for driver in self:
            if driver.license_expiry_date and driver.license_expiry_date < date.today():
                # ensure driver not available if license expired
                driver.status = 'off_duty'
