# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TransitopsVehicle(models.Model):
    _name = 'transitops.vehicle'
    _description = 'Vehicle'
    _order = 'name asc'

    name = fields.Char(string='Vehicle Name', required=True)
    registration_number = fields.Char(string='Registration Number', required=True)
    type = fields.Selection([
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('car', 'Car'),
    ], string='Type', default='truck', required=True)
    max_load_capacity = fields.Float(string='Max Load Capacity (kg)', required=True, default=0.0)
    status = fields.Selection([
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired'),
    ], string='Status', default='available', required=True)
    odometer = fields.Float(string='Odometer (km)', default=0.0)
    region = fields.Char(string='Region')

    # Relations to allow dependencies/computations
    fuel_log_ids = fields.One2many('transitops.fuel.log', 'vehicle_id', string='Fuel Logs')
    expense_ids = fields.One2many('transitops.expense', 'vehicle_id', string='Expenses')
    maintenance_ids = fields.One2many('transitops.maintenance', 'vehicle_id', string='Maintenance Records')
    trip_ids = fields.One2many('transitops.trip', 'vehicle_id', string='Trips')

    # Computed KPI fields (stored for pivot/graph views)
    total_operational_cost = fields.Float(string='Total Operational Cost ($)', compute='_compute_kpis', store=True)
    total_revenue = fields.Float(string='Total Revenue ($)', compute='_compute_kpis', store=True)
    roi = fields.Float(string='ROI ($)', compute='_compute_kpis', store=True)
    fuel_efficiency = fields.Float(string='Fuel Efficiency (km/L)', compute='_compute_kpis', store=True)

    @api.depends('fuel_log_ids.cost', 'fuel_log_ids.liters', 'expense_ids.cost', 'maintenance_ids.cost', 'trip_ids.revenue', 'trip_ids.status', 'trip_ids.planned_distance')
    def _compute_kpis(self):
        for vehicle in self:
            fuel_cost = sum(log.cost for log in vehicle.fuel_log_ids)
            fuel_liters = sum(log.liters for log in vehicle.fuel_log_ids)
            maint_cost = sum(maint.cost for maint in vehicle.maintenance_ids)
            expense_cost = sum(exp.cost for exp in vehicle.expense_ids)
            
            # Operational Cost
            vehicle.total_operational_cost = fuel_cost + maint_cost + expense_cost
            
            # Total Revenue
            completed_trips = vehicle.trip_ids.filtered(lambda t: t.status == 'completed')
            vehicle.total_revenue = sum(trip.revenue for trip in completed_trips)
            
            # ROI
            vehicle.roi = vehicle.total_revenue - vehicle.total_operational_cost
            
            # Fuel Efficiency (km/L)
            total_distance = sum(trip.planned_distance for trip in completed_trips)
            if fuel_liters > 0.0:
                vehicle.fuel_efficiency = total_distance / fuel_liters
            else:
                vehicle.fuel_efficiency = 0.0
