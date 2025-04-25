import uuid
from odoo import models, fields, api

class PartnerUUID(models.Model):
    _inherit = "res.partner"

    x_studio_uuid = fields.Char(string="UUID", readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('x_studio_uuid'):
            vals['x_studio_uuid'] = str(uuid.uuid4())
        return super(PartnerUUID, self).create(vals)

    def write(self, vals):
        for record in self:
            if not record.x_studio_uuid and 'x_studio_uuid' not in vals:
                vals['x_studio_uuid'] = str(uuid.uuid4())
        return super(PartnerUUID, self).write(vals)
