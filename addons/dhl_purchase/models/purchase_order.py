from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import base64

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'