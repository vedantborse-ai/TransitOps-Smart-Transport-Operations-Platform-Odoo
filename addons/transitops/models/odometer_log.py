# -*- coding: utf-8 -*-

from odoo import models, fields


class TransitopsVehicleOdometerLog(models.Model):
    _name = "transitops.vehicle.odometer.log"
    _description = "Vehicle Odometer Log"
    _order = "date desc, id desc"

    vehicle_id = fields.Many2one(
        "transitops.vehicle",
        string="Vehicle",
        required=True,
        ondelete="cascade"
    )

    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        required=True
    )

    value = fields.Float(
        string="Odometer Value",
        required=True
    )