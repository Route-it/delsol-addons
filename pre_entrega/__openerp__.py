# -*- coding: utf-8 -*-
{
    'name': "pre_entrega",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    "author": "Diego Richi",
    "website": "www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delsol_base'],

    # always loaded
    'data': [
        'security/actions_security.xml',
        'security/profile_security.xml',
        'security/ir.model.access.csv',
        'security/menu_security.xml',
        'views/vehicle.xml',
        'views/menu.xml',
        'data/events.xml',
        'data/ir_cron.xml',
        'data/parameters.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}