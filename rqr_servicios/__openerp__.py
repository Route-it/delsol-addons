# -*- coding: utf-8 -*-
{
    'name': "Gestion de RQR y llamados posteriores (servicios)",

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
    'depends': ['base','delsol_base','rqr','project','hr'],

    # always loaded
    'data': [
        'security/actions_security.xml',
        'security/profiles_security.xml',
        'security/menu_security.xml',
        'security/ir.model.access.csv',
        'views/call.xml',
        'views/delivery.xml',
        'views/rqr.xml',
        'views/menu.xml',
        'data/events.xml',
        'data/ir_cron.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}