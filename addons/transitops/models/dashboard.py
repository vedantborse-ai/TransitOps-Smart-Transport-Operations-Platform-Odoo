# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class TransitopsDashboard(models.Model):
    _name = 'transitops.dashboard'
    _description = 'Fleet KPI Dashboard'

    name = fields.Char(string='Name', default='Fleet Overview Dashboard')
    
    # KPI Computed Fields
    active_vehicles_count = fields.Integer(string='Active Vehicles', compute='_compute_kpis')
    available_vehicles_count = fields.Integer(string='Available Vehicles', compute='_compute_kpis')
    maintenance_vehicles_count = fields.Integer(string='Vehicles in Maintenance', compute='_compute_kpis')
    active_trips_count = fields.Integer(string='Active Trips', compute='_compute_kpis')
    pending_trips_count = fields.Integer(string='Pending Trips', compute='_compute_kpis')
    drivers_on_duty_count = fields.Integer(string='Drivers On Duty', compute='_compute_kpis')
    fleet_utilization_rate = fields.Float(string='Fleet Utilization (%)', compute='_compute_kpis')

    def _compute_kpis(self):
        for dashboard in self:
            # Gather vehicle statuses
            vehicles = self.env['transitops.vehicle'].search([])
            active_v = len(vehicles.filtered(lambda v: v.status == 'on_trip'))
            avail_v = len(vehicles.filtered(lambda v: v.status == 'available'))
            maint_v = len(vehicles.filtered(lambda v: v.status == 'in_shop'))

            dashboard.active_vehicles_count = active_v
            dashboard.available_vehicles_count = avail_v
            dashboard.maintenance_vehicles_count = maint_v

            # Gather trip statuses
            trips = self.env['transitops.trip'].search([])
            dashboard.active_trips_count = len(trips.filtered(lambda t: t.status == 'dispatched'))
            dashboard.pending_trips_count = len(trips.filtered(lambda t: t.status == 'draft'))

            # Gather drivers
            drivers = self.env['transitops.driver'].search([])
            dashboard.drivers_on_duty_count = len(drivers.filtered(lambda d: d.status in ('available', 'on_trip')))

            # Fleet Utilization
            total_active_pool = active_v + avail_v + maint_v
            if total_active_pool > 0:
                dashboard.fleet_utilization_rate = (active_v / total_active_pool) * 100.0
            else:
                dashboard.fleet_utilization_rate = 0.0

    @api.model
    def action_open_dashboard(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({})
        else:
            # Force recomputation of KPIs when dashboard is opened
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
