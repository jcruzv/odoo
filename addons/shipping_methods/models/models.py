from odoo import models, fields, api

class shipping_methods(models.Model):
    _name = 'shipping.methods'

    name = fields.Char(
        string='Nombre',
    )

    courier = fields.Char(
        string='Paquetería',
    )

    processedBy = fields.Char(
        string='Procesado por',
    )
    
    shipping_code = fields.Char(
        string='Código del producto de envío',
    )

    rate_id = fields.Char(
        string="ID de Cotización",
        help="Exclusivo para Skydropx"
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

    fuelSurcharge = fields.Float(
        string='Combustible',
    )
    
    remoteArea = fields.Float(
        string='Área Remota',
    )

    peakSeason = fields.Float(
        string='Temporada Alta',
    )

    other = fields.Float(
        string='Otros',
    )

    weight = fields.Float(
        string='Peso',
    )

    requestDate = fields.Datetime(
        string="Hora y Fecha de Solicitud",
    )

    origin = fields.Char(
        string='Origen',
        description='Origen del envío (ciudad)',
    )

    destination = fields.Char(
        string='Destino',
        description='Origen del envío (ciudad)',
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