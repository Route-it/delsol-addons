# -*- coding: utf-8 -*-
{
    'name': "entregas",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Diego Richi",
    'website': "http://www.diegorichi.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Del Sol',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','delsol_base','hr','mail'],

    # always loaded
    'data': [
        'security/menu_security.xml',
        'security/actions_security.xml',
        'security/profiles_security.xml',
        'security/ir.model.access.csv',
        'views/delivery.xml',
        'views/vehicle.xml',
        'views/res_partner_view.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}