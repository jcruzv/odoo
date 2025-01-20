# -*- coding: utf-8 -*-
{
    'name': 'Métodos de Envío de DHL',
    'description': 'Módulo para gestionar los métodos de envío de DHL en las órdenes de compra.',
    
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_view.xml',
        # 'views/templates.xml',
    ],
    'installable' : True,
    'application' : True,
}