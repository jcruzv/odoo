from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    onTime = fields.Selection([
        ('En tiempo', 'En tiempo'),
        ('Atrasado', 'Atrasado'),
    ], string='En tiempo', compute='_compute_on_time', store=True)

    date_filter = fields.Date(string='Fecha de filtro', default=fields.Date.today(), required=False)

    def _compute_on_time(self):
        hoy = datetime.now()
        for record in self:
            if record.state != "done" and hoy > record.scheduled_date or (record.date_done and (record.date_done - timedelta(hours=1)) > record.scheduled_date):
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