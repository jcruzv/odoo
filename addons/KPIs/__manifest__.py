# -*- coding: utf-8 -*-
{
    'name': "Dashboard KPIs",

    'summary': "Resumen díario de KPIs.",

    'description': """
        Dashboard KPIs es un módulo que permite visualizar y analizar los indicadores clave de rendimiento (KPIs) de una empresa en un solo lugar.
    """,

    'author': "Jorge Cruz",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Shipping',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_picking_menu.xml',
        # 'data/actions.xml',
    ],
    'assets': {
        'web.assets_frontend': [
        ],
        'web.assets_backend': [
            'KPIs/static/src/components/*/*',
            # '/dhl/static/src/css/custom_styles.css',
        ],
    },

    'installable' : True,
}