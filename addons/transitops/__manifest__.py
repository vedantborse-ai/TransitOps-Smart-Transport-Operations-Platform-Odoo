# -*- coding: utf-8 -*-
{
    'name': 'TransitOps - Smart Transport Operations Platform',
    'version': '1.0',
    'summary': 'Digitize vehicle, driver, dispatch, maintenance, and expense management.',
    'description': """
TransitOps Smart Transport Operations Platform
=============================================
Centralized platform to manage complete lifecycle of transport operations:
- Vehicle Registry & Lifecycle Status
- Driver Management & Compliance
- Trip Dispatching & Validation Rules
- Vehicle Maintenance Log & Auto-status update
- Fuel & Expense Management
- Analytics Dashboard (KPIs, Fuel Efficiency, ROI)
    """,
    'author': 'Hackathon Team',
    'category': 'Operations/Transportation',
    'depends': ['base', 'mail', 'portal'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/vehicle_views.xml',
        'views/driver_views.xml',
        'views/trip_views.xml',
        'views/maintenance_views.xml',
        'views/expense_views.xml',
        'views/dashboard_views.xml',
        'report/trip_report_templates.xml',
        'report/report_views.xml',
        'data/data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
