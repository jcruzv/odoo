{
    'name': 'Barcode Patch',
    'version': '1.0',
    'category': 'Warehouse',
    'author': 'Tu Nombre o Empresa',
    'website': 'https://www.tuwebsite.com',
    'summary': 'Modificación del módulo Barcode para personalización de escaneo.',
    'description': """
        Este módulo realiza modificaciones en la funcionalidad del módulo Barcode
        de Odoo para personalizar el procesamiento de códigos de barras, como la
        verificación de lotes y la actualización de líneas de picking.
    """,
    'depends': ['stock_barcode'],
    'data': [
        # Archivos XML o vistas adicionales si tienes
    ],
    'assets': {
        'web.assets_backend': [
            'barcode_patch/static/src/js/barcode_model_patch.js',  # Ruta de tu archivo JS
            'barcode_patch/static/src/js/barcode_picking_patch.js',  # Ruta de tu archivo JS
            'barcode_patch/static/src/js/barcode_service_patch.js',  # Ruta de tu archivo JS
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
