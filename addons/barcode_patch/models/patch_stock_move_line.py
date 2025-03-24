from odoo import models
import logging

_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _get_fields_stock_barcode(self):
        _logger.info('StockMoveLine._get_fields_stock_barcode called')
        original_fields = super(StockMoveLine, self)._get_fields_stock_barcode()
        _logger.info('StockMoveLine._get_fields_stock_barcode: %s', original_fields)
        additional_fields = [
            'x_studio_contenedor',
        ]
        return original_fields + additional_fields