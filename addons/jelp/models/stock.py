from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    track_state = fields.Selection(
        [('pending', 'Pendiente'), ('accepted', 'Aceptado'), ('branch_accepted', 'Sucursal Aceptada'),
         ('branch_in_progress', 'Sucursal en Progreso'), ('branch_dispatch', 'Sucursal Despachada'),
         ('driver_in_branch', 'Conductor en Sucursal'), ('supplied', 'Suministrado'), ('order_waiting', 'Esperando'),
         ('transit', 'En Tránsito'), ('onsite', 'En Sitio'), ('completed', 'Completado'),
         ('cancel_request', 'Solicitud de Cancelación'), ('canceled', 'Cancelado'),
         ('completed_request', 'Solicitud de Completado')],
        string='Estado del Seguimiento',
        default='pending',
        help="Estado del seguimiento del pedido.",
        store=True,
    )

    track_longitude = fields.Float(
        string='Longitud',
        help="Longitud de la ubicación del pedido.",
        store=True,
    )

    track_latitude = fields.Float(
        string='Latitud',
        help="Latitud de la ubicación del pedido.",
        store=True,
    )
    
    def request_jelp_location(self):
        """Request the location of the Jelp driver."""
    
        return False
    
    def action_open_custom_map_view(self):
        """Retorna la acción para mostrar la vista OWL relacionada con el seguimiento."""
        print(self.track_state, self.track_longitude, self.track_latitude)
        return {
            'type': 'ir.actions.client',
            'tag': 'custom_map_view',
            'target': 'new',  # Abre en una nueva ventana modal
            'context': {
                'track_state': self.track_state,
                'track_longitude': self.track_longitude,
                'track_latitude': self.track_latitude,
                'partner_longitude': self.partner_id.partner_longitude,
                'partner_latitude': self.partner_id.partner_latitude,
            },
        }