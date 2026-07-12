# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TransitopsTrip(models.Model):
    _name = 'transitops.trip'
    _description = 'Trip Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Trip Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'), tracking=True)
    source = fields.Char(string='Source Location', required=True, tracking=True)
    destination = fields.Char(string='Destination Location', required=True, tracking=True)
    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True, tracking=True)
    driver_id = fields.Many2one('transitops.driver', string='Driver', required=True, tracking=True)
    cargo_weight = fields.Float(string='Cargo Weight (kg)', required=True, tracking=True)
    planned_distance = fields.Float(string='Planned Distance (km)', required=True, tracking=True)
    revenue = fields.Float(string='Revenue ($)', required=True, tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, required=True, tracking=True)

    # Trip Completion Fields (only relevant after dispatch)
    final_odometer = fields.Float(string='Final Odometer (km)', tracking=True)
    fuel_consumed = fields.Float(string='Fuel Consumed (L)', tracking=True)
    fuel_cost = fields.Float(string='Fuel Cost ($)', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('transitops.trip') or _('New')
        return super(TransitopsTrip, self).create(vals_list)

    @api.constrains('cargo_weight', 'vehicle_id')
    def _check_cargo_weight(self):
        for record in self:
            if record.vehicle_id and record.cargo_weight > record.vehicle_id.max_load_capacity:
                raise ValidationError(_(
                    "Cargo weight (%s kg) cannot exceed the vehicle's maximum load capacity (%s kg)!"
                ) % (record.cargo_weight, record.vehicle_id.max_load_capacity))

    def action_dispatch(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_("Only draft trips can be dispatched."))
            if not record.vehicle_id or record.vehicle_id.status != 'available':
                raise ValidationError(_("The vehicle %s is not available (Current Status: %s).") % (
                    record.vehicle_id.name, record.vehicle_id.status
                ))
            if not record.driver_id or record.driver_id.status != 'available':
                raise ValidationError(_("The driver %s is not available (Current Status: %s).") % (
                    record.driver_id.name, record.driver_id.status
                ))
            if record.driver_id.license_expiry_date and record.driver_id.license_expiry_date < fields.Date.today():
                raise ValidationError(_("The driver %s's license has expired (Expiry: %s)!") % (
                    record.driver_id.name, record.driver_id.license_expiry_date
                ))
            
            record.status = 'dispatched'
            record.vehicle_id.status = 'on_trip'
            record.driver_id.status = 'on_trip'

    def action_complete(self):
        for record in self:
            if record.status != 'dispatched':
                raise ValidationError(_("Only dispatched trips can be marked as completed."))
            if record.final_odometer < record.vehicle_id.odometer:
                raise ValidationError(_(
                    "Final odometer (%s km) cannot be less than the vehicle's current odometer (%s km)!"
                ) % (record.final_odometer, record.vehicle_id.odometer))
            if record.fuel_consumed <= 0.0 or record.fuel_cost <= 0.0:
                raise ValidationError(_("Fuel consumed and cost must be greater than zero!"))
            
            # Create fuel log record
            self.env['transitops.fuel.log'].create({
                'vehicle_id': record.vehicle_id.id,
                'liters': record.fuel_consumed,
                'cost': record.fuel_cost,
                'date': fields.Date.today(),
            })

            # Update vehicle odometer and status
            record.vehicle_id.odometer = record.final_odometer
            record.vehicle_id.status = 'available'
            
            # Update driver status
            record.driver_id.status = 'available'
            
            # Complete the trip
            record.status = 'completed'

    def action_cancel(self):
        for record in self:
            if record.status not in ('draft', 'dispatched'):
                raise ValidationError(_("Only draft or dispatched trips can be cancelled."))
            
            # Free up vehicle and driver if the trip was already dispatched
            if record.status == 'dispatched':
                if record.vehicle_id.status == 'on_trip':
                    record.vehicle_id.status = 'available'
                if record.driver_id.status == 'on_trip':
                    record.driver_id.status = 'available'
            
            record.status = 'cancelled'
