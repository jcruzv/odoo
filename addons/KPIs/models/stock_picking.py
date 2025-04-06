from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    onTime = fields.Selection([
        ('En tiempo', 'En tiempo'),
        ('Atrasado', 'Atrasado'),
    ], string='En tiempo', compute='_compute_on_time', store=True)

    date_filter = fields.Date(string='Fecha de filtro', default=fields.Date.today(), required=False)

    @api.depends('scheduled_date', 'date_done', 'state')
    def _compute_on_time(self):
        hoy = datetime.now()
        for record in self:
            _logger.info(f"Record: {record}, Scheduled Date: {record.scheduled_date}, Date Done: {record.date_done}, State: {record.state}, Hoy: {hoy}")
            if record.state != "done" and (record.date_done or hoy) - timedelta(hours=1) > record.scheduled_date:
                record.onTime = 'Atrasado'
            else:
                record.onTime = 'En tiempo'
    
    def on_date_filter_change(self):
        print("on_date_filter_change")
        return False
    
    def action_open_custom_kpis(self):
        """Retorna la acción para mostrar la vista OWL relacionada con el seguimiento."""
        print(self.track_state, self.track_longitude, self.track_latitude)
        return {
            'type': 'ir.actions.client',
            'tag': 'custom_kpis',
            'context': {
            },
        }