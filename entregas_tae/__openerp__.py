# -*- coding: utf-8 -*-
{
    'name': "entregas_tae",

    'summary': """
        obtiene el estado de los vehiculos en FIS""",

    'description': """
        obtiene el estado de los vehiculos en FIS
    """,

    'author': "Diego Richi",
    'website': "http://www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delsol_base','entregas','delsol_events'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/parameters.xml',
        'views/delivery.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}