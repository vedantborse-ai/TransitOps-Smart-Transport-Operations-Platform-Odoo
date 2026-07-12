{
    'name': 'TransitOps - Smart Transport Operations Platform',
    'version': '17.0.1.0.0',
    'category': 'Operations/Transportation',
    'summary': 'Smart Transport Operations Platform',
    'depends': [
        'base',
        'mail',
        'portal',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/vehicle_views.xml',
    ],
    'installable': True,
    'application': True,
}
