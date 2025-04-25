from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class StockWarehouseOrderpointPatch(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.depends('qty_multiple', 'qty_forecast', 'product_min_qty', 'product_max_qty', 'visibility_days')
    def _compute_qty_to_order_computed(self):
        orderpoints_to_compute = self.filtered(lambda orderpoint: orderpoint.product_id and orderpoint.location_id)
        qty_in_progress_by_orderpoint = orderpoints_to_compute._quantity_in_progress()
        for orderpoint in self:
            # Obtener el producto
            product = orderpoint.product_id
            # Verificar si el producto tiene el campo x_studio_cajas_x_tarima
            if hasattr(product, 'x_studio_cajas_x_tarima'):
                _logger.info(f"Product {product.name} has x_studio_cajas_x_tarima: {product.x_studio_cajas_x_tarima}")
                if product.x_studio_cajas_x_tarima != 0:
                    if orderpoint.qty_forecast != orderpoint.qty_on_hand + orderpoint.product_id.x_studio_cajas_x_tarima and orderpoint.qty_on_hand < orderpoint.product_min_qty and orderpoint.qty_to_order != orderpoint.product_id.x_studio_cajas_x_tarima:
                        orderpoint.write({
                            "qty_to_order_manual" : orderpoint.product_id.x_studio_cajas_x_tarima
                        })
            else:
                _logger.info(f"Product {product.name} does not have x_studio_cajas_x_tarima")
            # Calcular qty_to_order_computed
            orderpoint.qty_to_order_computed = orderpoint._get_qty_to_order(qty_in_progress_by_orderpoint=qty_in_progress_by_orderpoint)
        (self - orderpoints_to_compute).qty_to_order_computed = False