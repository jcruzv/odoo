from odoo import models, fields, api

class campaigns(models.Model):
    _name = 'purchase.campaigns'

    name = fields.Char(
        string='Nombre',
    )
    
    start = fields.Datetime(
        string='Inicio',
        default=fields.Datetime.now,
    )

    end = fields.Datetime(
        string='Fin',
        default=fields.Datetime.now,
    )
    
    active = fields.Boolean(
        string='Activa',
        default=True,
    )

    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Productos',
    )