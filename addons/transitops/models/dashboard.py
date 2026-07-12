# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TransitopsDashboard(models.Model):
    _name = 'transitops.dashboard'
    _description = 'Fleet KPI Dashboard'

    name = fields.Char(string='Name', default='Fleet Overview Dashboard')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Existing KPI Computed Fields (to preserve compatibility)
    active_vehicles_count = fields.Integer(string='Active Vehicles', compute='_compute_kpis')
    available_vehicles_count = fields.Integer(string='Available Vehicles', compute='_compute_kpis')
    maintenance_vehicles_count = fields.Integer(string='Vehicles in Maintenance', compute='_compute_kpis')
    active_trips_count = fields.Integer(string='Active Trips', compute='_compute_kpis')
    pending_trips_count = fields.Integer(string='Pending Trips', compute='_compute_kpis')
    drivers_on_duty_count = fields.Integer(string='Drivers On Duty', compute='_compute_kpis')
    fleet_utilization_rate = fields.Float(string='Fleet Utilization (%)', compute='_compute_kpis')

    # Enhanced Fleet Analytics KPI Fields
    total_vehicles_count = fields.Integer(string='Total Vehicles', compute='_compute_kpis')
    vehicles_on_trip_count = fields.Integer(string='Vehicles Currently On Trip', compute='_compute_kpis')
    vehicles_in_maintenance_count = fields.Integer(string='Vehicles In Maintenance', compute='_compute_kpis')
    
    total_drivers_count = fields.Integer(string='Total Drivers', compute='_compute_kpis')
    drivers_available_count = fields.Integer(string='Drivers Currently Available', compute='_compute_kpis')
    drivers_on_trip_count = fields.Integer(string='Drivers On Trip', compute='_compute_kpis')
    
    total_trips_count = fields.Integer(string='Total Trips', compute='_compute_kpis')
    dispatched_trips_count = fields.Integer(string='Active Trips (Dispatched)', compute='_compute_kpis')
    completed_trips_count = fields.Integer(string='Completed Trips', compute='_compute_kpis')
    cancelled_trips_count = fields.Integer(string='Cancelled Trips', compute='_compute_kpis')
    
    total_revenue = fields.Monetary(string='Total Revenue', compute='_compute_kpis', currency_field='currency_id')
    total_fuel_cost = fields.Monetary(string='Total Fuel Cost', compute='_compute_kpis', currency_field='currency_id')
    total_maintenance_cost = fields.Monetary(string='Total Maintenance Cost', compute='_compute_kpis', currency_field='currency_id')
    total_operational_cost = fields.Monetary(string='Total Operational Cost', compute='_compute_kpis', currency_field='currency_id')
    
    avg_fuel_efficiency = fields.Float(string='Average Fuel Efficiency (km/L)', compute='_compute_kpis')
    avg_driver_safety_score = fields.Float(string='Average Driver Safety Score', compute='_compute_kpis')

    def _compute_kpis(self):
        for dashboard in self:
            VehicleObj = self.env['transitops.vehicle']
            DriverObj = self.env['transitops.driver']
            TripObj = self.env['transitops.trip']
            FuelObj = self.env['transitops.fuel.log']
            MaintObj = self.env['transitops.maintenance']
            ExpenseObj = self.env['transitops.expense']

            # 1. Vehicle KPI Calculations
            total_vehicles = VehicleObj.search_count([])
            avail_v = VehicleObj.search_count([('status', '=', 'available')])
            on_trip_v = VehicleObj.search_count([('status', '=', 'on_trip')])
            in_shop_v = VehicleObj.search_count([('status', '=', 'in_shop')])
            
            dashboard.total_vehicles_count = total_vehicles
            dashboard.available_vehicles_count = avail_v
            dashboard.vehicles_on_trip_count = on_trip_v
            dashboard.vehicles_in_maintenance_count = in_shop_v
            dashboard.active_vehicles_count = on_trip_v
            dashboard.maintenance_vehicles_count = in_shop_v

            # 2. Driver KPI Calculations
            total_drivers = DriverObj.search_count([])
            avail_drivers = DriverObj.search_count([('status', '=', 'available')])
            on_trip_drivers = DriverObj.search_count([('status', '=', 'on_trip')])
            
            dashboard.total_drivers_count = total_drivers
            dashboard.drivers_available_count = avail_drivers
            dashboard.drivers_on_trip_count = on_trip_drivers
            dashboard.drivers_on_duty_count = DriverObj.search_count([('status', 'in', ('available', 'on_trip'))])

            # 3. Trip KPI Calculations
            total_trips = TripObj.search_count([])
            draft_trips = TripObj.search_count([('status', '=', 'draft')])
            dispatched_trips = TripObj.search_count([('status', '=', 'dispatched')])
            completed_trips = TripObj.search_count([('status', '=', 'completed')])
            cancelled_trips = TripObj.search_count([('status', '=', 'cancelled')])

            dashboard.total_trips_count = total_trips
            dashboard.active_trips_count = dispatched_trips
            dashboard.dispatched_trips_count = dispatched_trips
            dashboard.pending_trips_count = draft_trips
            dashboard.completed_trips_count = completed_trips
            dashboard.cancelled_trips_count = cancelled_trips

            # 4. Financial Calculations using aggregations
            revenue_res = TripObj.read_group([('status', '=', 'completed')], ['revenue'], [])
            dashboard.total_revenue = revenue_res[0]['revenue'] if revenue_res and revenue_res[0]['revenue'] else 0.0

            fuel_res = FuelObj.read_group([], ['cost'], [])
            dashboard.total_fuel_cost = fuel_res[0]['cost'] if fuel_res and fuel_res[0]['cost'] else 0.0

            maint_res = MaintObj.read_group([], ['cost'], [])
            dashboard.total_maintenance_cost = maint_res[0]['cost'] if maint_res and maint_res[0]['cost'] else 0.0

            expense_res = ExpenseObj.read_group([], ['cost'], [])
            total_expense = expense_res[0]['cost'] if expense_res and expense_res[0]['cost'] else 0.0

            dashboard.total_operational_cost = dashboard.total_fuel_cost + dashboard.total_maintenance_cost + total_expense

            # 5. Fleet Utilization Calculation (Vehicles On Trip / Active Vehicles) * 100
            # Active vehicles are those with status != 'retired'
            active_vehicles_count = VehicleObj.search_count([('status', '!=', 'retired')])
            if active_vehicles_count > 0:
                dashboard.fleet_utilization_rate = (on_trip_v / active_vehicles_count) * 100.0
            else:
                dashboard.fleet_utilization_rate = 0.0

            # 6. Averages
            vehicles_data = VehicleObj.search_read([('status', '!=', 'retired')], ['fuel_efficiency'])
            if vehicles_data:
                dashboard.avg_fuel_efficiency = sum(v['fuel_efficiency'] for v in vehicles_data) / len(vehicles_data)
            else:
                dashboard.avg_fuel_efficiency = 0.0

            drivers_data = DriverObj.search_read([('active', '=', True)], ['safety_score'])
            if drivers_data:
                dashboard.avg_driver_safety_score = sum(d['safety_score'] for d in drivers_data) / len(drivers_data)
            else:
                dashboard.avg_driver_safety_score = 0.0

    @api.model
    def action_open_dashboard(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({})
        else:
            record._compute_kpis()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fleet KPIs & Dashboard',
            'res_model': 'transitops.dashboard',
            'view_mode': 'form',
            'res_id': record.id,
            'target': 'current',
            'flags': {'initial_mode': 'readonly', 'form_view_ref': 'transitops.view_transitops_dashboard_form'},
        }
