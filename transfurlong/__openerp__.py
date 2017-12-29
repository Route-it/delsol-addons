# -*- coding: utf-8 -*-
{
    'name': "transfurlong",

    'summary': """
        obtiene el estado de los vehiculos en transfurlong""",

    'description': """
        obtiene el estado de los vehiculos en transfurlong
    """,

    'author': "Diego Richi",
    'website': "http://www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delsol_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/vehicle.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}