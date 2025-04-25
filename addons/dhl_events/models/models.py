from odoo import models, fields, api

class shipping_methods(models.Model):
    _name = 'dhl.shipping.events'

    purchase_order = fields.Many2one(
        string='Orden de Compra',
        comodel_name='purchase.order',
        ondelete='cascade',
    )

    track_number = fields.Char(
        string='Número de seguimiento',
    )

    name = fields.Char(
        string='Nombre',
    )
    
    date = fields.Date(
        string='Fecha',
    )

    time = fields.Char(
        string='Hora',
    )
    
    code = fields.Char(
        string='Codigo',
    )