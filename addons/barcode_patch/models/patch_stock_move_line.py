from odoo import models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_fields_stock_barcode(self):
        fields = super()._get_fields_stock_barcode()
        fields.append('x_studio_contenedor')
        return fields
