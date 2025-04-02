
from odoo import http
from odoo.http import request

class MapController(http.Controller):
    @http.route('/map', type='http', auth='user', website=True)
    def map(self, **kw):
        return request.render('map.map_template', {})
