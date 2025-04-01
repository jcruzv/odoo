# -*- coding: utf-8 -*-
{
    'name': "Generador de Envíos",

    'summary': "Generador de envíos mediante la API de DHL y envía, con la posibilidad de añadir eventos y campañas.",

    'description': """
        Este módulo permite la integración con la API de DHL para la generación automática de envíos desde Odoo. 
        Facilita la creación y gestión de envíos, permitiendo a los usuarios añadir eventos y campañas asociadas a los pedidos de compra. 
        Además, incluye vistas personalizadas para la gestión de órdenes de compra filtradas y estilos personalizados para la interfaz de usuario.
    """,

    'author': "Jorge Cruz",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Shipping',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'shipping_methods', 'shipping_events', 'campaigns', 'product'],

    # always loaded
    'data': [
        'views/purchase_order_views.xml',
        'views/filtered_purchase_order_menu.xml',
        # 'data/actions.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # '/dhl/static/src/css/custom_styles.css',
        ],
        'web.assets_backend': [
            # '/dhl/static/src/css/custom_styles.css',
        ],
    },

    'installable' : True,
    'application' : True,
}