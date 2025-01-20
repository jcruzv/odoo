from odoo import models, fields

class ShippingMethod(models.Model):
    _name = 'shipping.method'
    _description = 'Métodos de Envío de DHL'

    name = fields.Char('Nombre del Método de Envío', required=True)
    dhl_code = fields.Char('Código de DHL', required=True)
    price = fields.Float('Precio', required=True)
