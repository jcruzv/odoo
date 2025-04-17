from odoo import models, api
from odoo.tools.misc import groupby
from odoo.tools.float_utils import float_compare

class StockMoveNoMerge(models.Model):
    _inherit = "stock.move"

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        grouped_moves = groupby(self, key=lambda m: m._key_assign_picking())
        for group, moves in grouped_moves:
            moves = self.env['stock.move'].concat(*moves)
            new_picking = True
            # Could pass the arguments contained in group but they are the same
            # for each move that why moves[0] is acceptable
            picking = moves[0]._search_picking_for_assignation()
            
            # Don't create picking for negative moves since they will be
            # reverse and assign to another picking
            moves = moves.filtered(lambda m: float_compare(m.product_uom_qty, 0.0, precision_rounding=m.product_uom.rounding) >= 0)
            if not moves:
                continue
            new_picking = True
            picking = Picking.create(moves._get_new_picking_values())

            moves.write({'picking_id': picking.id})
            moves._assign_picking_post_process(new=new_picking)
        return True