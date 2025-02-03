# -*- coding: utf-8 -*-
{
    'name': "DHL Express",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'dhl_methods', 'dhl_events', 'campaigns', 'product'],

    # always loaded
    'data': [
        'views/purchase_order_views.xml',
        'views/filtered_purchase_order_menu.xml',
        # 'data/actions.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/dhl/static/src/css/custom_styles.css',
        ],
        'web.assets_backend': [
            '/dhl/static/src/css/custom_styles.css',
        ],
    },

    'installable' : True,
    'application' : True,
}