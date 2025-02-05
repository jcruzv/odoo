# -*- coding: utf-8 -*-
{
    'name': "Métodos de Envío",

    'summary': "Lista de métodos de envío proporcionados por el proveedor",

    'description': "Registro con el listado de métodos de envío proporcionados por el proveedor con los detalles de cada uno de ellos.",

    'author': "Jorge Cruz",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Shipping',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}