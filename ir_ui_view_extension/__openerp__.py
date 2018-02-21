# -*- coding: utf-8 -*-
{
    'name': "View Extension",

    'summary': """
        permite utilizar parametros para vistas que se abren desde otras vistas""",

    'description': """
        Permite ocultar, poner en solo lectura campos de vistas mediate context
    """,

    'author': "Route IT",
    'website': "http://www.routeit.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}