# -*- coding: utf-8 -*-
{
    'name': 'TransitOps',
    'version': '1.0',
    'summary': 'Smart Transport Operations Platform',
    'description': """
        Smart Transport Operations Platform for managing fleet, maintenance, fuel logs, and trips.
    """,
    'category': 'Transportation',
    'author': 'Antigravity',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/trip_views.xml',
        'views/expense_views.xml',
        'views/maintenance_views.xml',
        'views/dashboard_views.xml',
        'report/report_views.xml',
        'report/trip_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
