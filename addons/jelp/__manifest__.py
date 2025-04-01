# -*- coding: utf-8 -*-
{
    'name': "Rastreo de Envío JELP",

    'summary': "Integración de Jelp para el rastreo de envíos",

    'description': """
        Este módulo permite la integración de Jelp para el rastreo de envíos en Odoo.
        Permite a los usuarios rastrear las órdenes creadas en WMS.
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
        # 'views/menu.xml',
        'views/track_view.xml',
        'views/custom_map_view_action.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # '/dhl/static/src/css/custom_styles.css',
        ],
        'web.assets_backend': [
            'jelp/static/src/components/*/*',  # Ensure this file is included
            # 'jelp/static/src/js/main.js',
        ],
    },

    'installable' : True,
}