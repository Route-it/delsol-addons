# -*- coding: utf-8 -*-
{
    'name': "entregas_photos",

    'summary': """
        Muestra fotos de la entrega y se las envia al cliente.""",

    'description': """
        Muestra fotos de la entrega y se las envia al cliente.
    """,

    'author': "Diego Richi",
    'website': "http://www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delsol_base','entregas'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/delivery.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}