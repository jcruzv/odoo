from odoo import models, fields, api

class shipping_methods(models.Model):
    _name = 'dhl.shipping.methods'

    name = fields.Char(
        string='Nombre',
    )
    
    dhl_code = fields.Char(
        string='Código del producto de DHL',
    )

    price = fields.Float(
        string='Precio',
    )
    
    purchase_order = fields.Many2one(
        string='purchase_order',
        comodel_name='purchase.order',
        ondelete='cascade',
    )
    
    basePrice = fields.Float(
        string='Precio Base',
    )
    
    discount = fields.Float(
        string='Descuento',
    )

    tax = fields.Float(
        string='Impuesto',
    )
    
    # envio = fields.Float(
    #     string='Costo Envío',
    # )
    
    # area = fields.Float(
    #     string='Área Remota',
    # )
    
    # gas = fields.Float(
    #     string='Combustible',
    # )