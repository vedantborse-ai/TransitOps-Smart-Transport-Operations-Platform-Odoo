# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TransitopsVehicle(models.Model):
    _name = 'transitops.vehicle'
    _description = 'Vehicle Registry'
    _order = 'registration_number'

    name = fields.Char(string='Model Name', required=True)
    registration_number = fields.Char(string='Registration Number', required=True)
    type = fields.Selection([
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('bus', 'Bus'),
    ], string='Vehicle Type', required=True, default='van')
    max_load_capacity = fields.Float(string='Max Load Capacity (kg)', required=True)
    odometer = fields.Float(string='Odometer (km)', default=0.0)
    acquisition_cost = fields.Float(string='Acquisition Cost ($)', default=0.0)
    region = fields.Char(string='Region', default='Default')
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired'),
    ], string='Status', default='available', required=True, tracking=True)
    active = fields.Boolean(default=True)

    # Document management & specifications (bonus features)
    brand = fields.Char(string='Brand')
    manufacture_year = fields.Integer(string='Manufacture Year')
    fuel_type = fields.Selection([
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ], string='Fuel Type', default='diesel')
    registration_document = fields.Binary(string='Registration Certificate')
    insurance_document = fields.Binary(string='Insurance Policy')

    fuel_log_ids = fields.One2many('transitops.fuel.log', 'vehicle_id', string='Fuel Logs')
    expense_ids = fields.One2many('transitops.expense', 'vehicle_id', string='Expenses')
    trip_ids = fields.One2many('transitops.trip', 'vehicle_id', string='Trips')
    maintenance_ids = fields.One2many('transitops.maintenance', 'vehicle_id', string='Maintenance Records')
    odometer_log_ids = fields.One2many('transitops.vehicle.odometer.log', 'vehicle_id', string='Odometer Logs')

    total_operational_cost = fields.Float(string='Total Operational Cost ($)', compute='_compute_operational_cost', store=True)
    fuel_efficiency = fields.Float(string='Fuel Efficiency (km/L)', compute='_compute_fuel_efficiency', store=True)
    total_revenue = fields.Float(string='Total Revenue ($)', compute='_compute_total_revenue', store=True)
    roi = fields.Float(string='Vehicle ROI (%)', compute='_compute_roi', store=True)

    _sql_constraints = [
        ('unique_registration_number', 'unique(registration_number)', 'The vehicle registration number must be unique!'),
    ]

    @api.depends('fuel_log_ids.cost', 'expense_ids.cost', 'maintenance_ids.cost', 'maintenance_ids.status')
    def _compute_operational_cost(self):
        for vehicle in self:
            fuel_cost = sum(vehicle.fuel_log_ids.mapped('cost'))
            other_expense_cost = sum(vehicle.expense_ids.mapped('cost'))
            # Include closed/completed maintenance costs
            maintenance_cost = sum(vehicle.maintenance_ids.filtered(lambda m: m.status == 'closed').mapped('cost'))
            vehicle.total_operational_cost = fuel_cost + other_expense_cost + maintenance_cost

    @api.depends('trip_ids.status', 'trip_ids.planned_distance', 'fuel_log_ids.liters')
    def _compute_fuel_efficiency(self):
        for vehicle in self:
            completed_trips = vehicle.trip_ids.filtered(lambda t: t.status == 'completed')
            total_distance = sum(completed_trips.mapped('planned_distance'))
            total_fuel = sum(vehicle.fuel_log_ids.mapped('liters'))
            vehicle.fuel_efficiency = total_distance / total_fuel if total_fuel > 0 else 0.0

    @api.depends('trip_ids.status', 'trip_ids.revenue')
    def _compute_total_revenue(self):
        for vehicle in self:
            completed_trips = vehicle.trip_ids.filtered(lambda t: t.status == 'completed')
            vehicle.total_revenue = sum(completed_trips.mapped('revenue'))

    @api.depends('total_revenue', 'total_operational_cost', 'acquisition_cost')
    def _compute_roi(self):
        for vehicle in self:
            if vehicle.acquisition_cost > 0:
                # ROI = (Revenue - (Maintenance + Fuel)) / Acquisition Cost * 100
                # total_operational_cost already includes Maintenance and Fuel
                vehicle.roi = ((vehicle.total_revenue - vehicle.total_operational_cost) / vehicle.acquisition_cost) * 100.0
            else:
                vehicle.roi = 0.0

    def write(self, vals):
        res = super(TransitopsVehicle, self).write(vals)
        if 'odometer' in vals:
            for vehicle in self:
                self.env['transitops.vehicle.odometer.log'].create({
                    'vehicle_id': vehicle.id,
                    'value': vehicle.odometer,
                })
        return res
