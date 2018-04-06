# -*- coding: utf-8 -*-
{
    'name': "Gestion de Entregas",

    'summary': """
        Modulo de trackeo RQRS Ford""",

    'description': """
        Con este modulo se aborda el trackeo de la recepción de RQR´s de parte de los clientes de la concesionaria Ford desde el momento de 
        la emisión del remito de entrega del vehículo hasta la encuesta realizada por Ford. 
    """,

    'author': "RouteIT",
    'website': "http://www.routeit.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','hr','mail'],

    # always loaded
    'data': [
        'security/rqr_security.xml',
        'security/ir.model.access.csv',
        'views/delivery.xml',
        'views/call.xml',
        'views/rqr.xml',
        'views/res_partner_view.xml',
        'views/vehicle.xml',
        'views/menu.xml',
        'report/report.xml',
        'data/events.xml',
        'data/ir_cron.xml',
        'data/view.xml',
        'data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}