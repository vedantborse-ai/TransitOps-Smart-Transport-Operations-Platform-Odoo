# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TransitopsTrip(models.Model):
    _name = 'transitops.trip'
    _description = 'Trip Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Trip Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    source = fields.Char(string='Source Address', required=True, tracking=True)
    destination = fields.Char(string='Destination Address', required=True, tracking=True)
    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True, tracking=True)
    driver_id = fields.Many2one('transitops.driver', string='Driver', required=True, tracking=True)
    cargo_weight = fields.Float(string='Cargo Weight (kg)', required=True, tracking=True)
    planned_distance = fields.Float(string='Planned Distance (km)', required=True, tracking=True)
    revenue = fields.Float(string='Revenue ($)', required=True, default=0.0, tracking=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, readonly=True)

    # Fields for completion step
    final_odometer = fields.Float(string='Final Odometer (km)', tracking=True)
    fuel_consumed = fields.Float(string='Fuel Consumed (Liters)', tracking=True)
    fuel_cost = fields.Float(string='Fuel Cost ($)', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('transitops.trip') or _('New')
        return super(TransitopsTrip, self).create(vals_list)

    @api.constrains('cargo_weight', 'vehicle_id')
    def _check_cargo_weight(self):
        for trip in self:
            if trip.vehicle_id and trip.cargo_weight > trip.vehicle_id.max_load_capacity:
                raise ValidationError(_(
                    "Cargo weight (%s kg) cannot exceed the vehicle's maximum load capacity (%s kg)!"
                ) % (trip.cargo_weight, trip.vehicle_id.max_load_capacity))

    @api.constrains('vehicle_id', 'driver_id', 'status')
    def _check_vehicle_driver_availability(self):
        for trip in self:
            if trip.status == 'dispatched':
                # Check vehicle status
                if trip.vehicle_id.status != 'available' and trip.vehicle_id.status != 'on_trip':
                    raise ValidationError(_("The vehicle %s is not available (Current status: %s).") % (
                        trip.vehicle_id.registration_number, trip.vehicle_id.status
                    ))
                # Check driver status
                if trip.driver_id.status != 'available' and trip.driver_id.status != 'on_trip':
                    raise ValidationError(_("The driver %s is not available (Current status: %s).") % (
                        trip.driver_id.name, trip.driver_id.status
                    ))
                # Check driver license expiry
                if trip.driver_id.is_license_expired:
                    raise ValidationError(_("The driver %s has an expired license and cannot be assigned!") % (
                        trip.driver_id.name
                    ))

    def action_dispatch(self):
        for trip in self:
            if trip.status != 'draft':
                raise ValidationError(_("Only draft trips can be dispatched."))
            
            # Double check status and license rules
            if trip.vehicle_id.status in ('in_shop', 'retired'):
                raise ValidationError(_("Vehicle is In Shop or Retired. Cannot dispatch."))
            if trip.driver_id.status == 'suspended' or trip.driver_id.is_license_expired:
                raise ValidationError(_("Driver is Suspended or has an Expired License. Cannot dispatch."))
            if trip.vehicle_id.status == 'on_trip':
                raise ValidationError(_("Vehicle is already on another active trip."))
            if trip.driver_id.status == 'on_trip':
                raise ValidationError(_("Driver is already on another active trip."))

            # Update statuses
            trip.vehicle_id.status = 'on_trip'
            trip.driver_id.status = 'on_trip'
            trip.status = 'dispatched'

    def action_complete(self):
        for trip in self:
            if trip.status != 'dispatched':
                raise ValidationError(_("Only dispatched trips can be completed."))
            
            # Ensure completion info is provided
            if trip.final_odometer <= 0.0 or trip.fuel_consumed <= 0.0:
                raise ValidationError(_("Please provide a valid final odometer reading and fuel consumed details to complete the trip."))
            
            if trip.final_odometer <= trip.vehicle_id.odometer:
                raise ValidationError(_("Final odometer (%s km) must be greater than the vehicle's current odometer (%s km).") % (
                    trip.final_odometer, trip.vehicle_id.odometer
                ))

            # Update vehicle odometer
            trip.vehicle_id.odometer = trip.final_odometer

            # Create Fuel Log automatically
            self.env['transitops.fuel.log'].create({
                'vehicle_id': trip.vehicle_id.id,
                'liters': trip.fuel_consumed,
                'cost': trip.fuel_cost or (trip.fuel_consumed * 1.5), # fallback estimate cost if not provided
                'date': fields.Date.context_today(self),
            })

            # Restore vehicle and driver to available
            trip.vehicle_id.status = 'available'
            trip.driver_id.status = 'available'
            trip.status = 'completed'

    def action_cancel(self):
        for trip in self:
            if trip.status not in ('draft', 'dispatched'):
                raise ValidationError(_("Only draft or dispatched trips can be cancelled."))
            
            if trip.status == 'dispatched':
                # Restore statuses if dispatched
                trip.vehicle_id.status = 'available'
                trip.driver_id.status = 'available'
                
            trip.status = 'cancelled'

    def unlink(self):
        for trip in self:
            if trip.status == 'dispatched':
                if trip.vehicle_id and trip.vehicle_id.status == 'on_trip':
                    trip.vehicle_id.status = 'available'
                if trip.driver_id and trip.driver_id.status == 'on_trip':
                    trip.driver_id.status = 'available'
        return super(TransitopsTrip, self).unlink()
