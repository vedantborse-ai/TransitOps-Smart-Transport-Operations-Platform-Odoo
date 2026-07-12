# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TransitopsMaintenance(models.Model):
    _name = 'transitops.maintenance'
    _description = 'Maintenance Record'
    _order = 'date desc'

    name = fields.Char(string='Maintenance Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    vehicle_id = fields.Many2one('transitops.vehicle', string='Vehicle', required=True)
    description = fields.Text(string='Maintenance Details/Description', required=True)
    cost = fields.Float(string='Cost ($)', default=0.0)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', required=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('transitops.maintenance') or _('New')
        records = super(TransitopsMaintenance, self).create(vals_list)
        # If created in progress directly
        for record in records:
            if record.status == 'in_progress':
                record.vehicle_id.status = 'in_shop'
        return records

    def write(self, vals):
        # Track status changes to transition vehicle statuses
        res = super(TransitopsMaintenance, self).write(vals)
        if 'status' in vals or 'vehicle_id' in vals:
            for record in self:
                if record.status == 'in_progress':
                    # Set vehicle to In Shop
                    if record.vehicle_id.status != 'in_shop':
                        record.vehicle_id.status = 'in_shop'
                elif record.status == 'closed':
                    # Restore vehicle to Available (unless retired)
                    if record.vehicle_id.status == 'in_shop':
                        record.vehicle_id.status = 'available'
        return res

    def action_start(self):
        for record in self:
            if record.status != 'draft':
                raise ValidationError(_("Maintenance can only start from draft status."))
            if record.vehicle_id.status == 'on_trip':
                raise ValidationError(_("Vehicle %s is currently on a trip and cannot enter maintenance.") % record.vehicle_id.registration_number)
            record.status = 'in_progress'
            record.vehicle_id.status = 'in_shop'

    def action_close(self):
        for record in self:
            if record.status != 'in_progress':
                raise ValidationError(_("Maintenance can only be closed if it is in progress."))
            record.status = 'closed'
            if record.vehicle_id.status == 'in_shop':
                record.vehicle_id.status = 'available'

    def unlink(self):
        for record in self:
            if record.status == 'in_progress':
                if record.vehicle_id and record.vehicle_id.status == 'in_shop':
                    record.vehicle_id.status = 'available'
        return super(TransitopsMaintenance, self).unlink()
