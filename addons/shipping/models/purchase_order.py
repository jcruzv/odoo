from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import io
import zipfile
import requests
import json 
import base64
import math
import asyncio
import aiohttp

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_shipping_events_action(self):
        """Retorna la acción para mostrar los eventos relacionados con la orden de compra."""
        self.ensure_one()  # Asegúrate de que solo se está llamando en un registro
        action = self.env.ref('shipping_events.action_shipping_|events_view').read()[0]
        action['domain'] = [('purchase_order', '=', self.id)]
        return action

    shipping_method = fields.Many2one(
        'shipping.methods',
        domain=[],
        string='Método de Envío',
        help='Selecciona un método de envío basado en las cotizaciones.'
    )


    customer_name = fields.Char(
        related='customer_id.name', 
        string="Cliente", 
        store=True
    )

    customer_zip = fields.Char(
        related='customer_id.zip', 
        string="Código Postal", 
        store=True
    )
    customer_state = fields.Char(
        related='customer_id.state_id.name', 
        string="Estado", 
        store=True
    )
    customer_city = fields.Char(
        related='customer_id.city', 
        string="Localidad", 
        store=True
    )
    
    shipping_quote = fields.Float(string='Total Envío', readonly=True)
    
    shipping_status = fields.Char(
        string='shipping_status',
    )        

    requestShipping = fields.Boolean(
        string='Solicitar Guía',
        help='Marcar si esta orden de compra requerirá la generación de una Guia de Envío.',
    )

    weight = fields.Float(
        string='Peso',
    )
    
    width = fields.Float(
        string='Ancho',
    )
    
    length = fields.Float(
        string='Largo',
    )
    
    height = fields.Float(
        string='Alto',
    ) 

    pesoVolumetrico = fields.Float(
        string='Peso Volumetrico',
        compute='_compute_peso_vol',
        store=True,
    )
    
    pesoMasa = fields.Float(
        string='Peso Masa',
        compute='_compute_peso_masa',
        store=True,
    )
    
    pesoEnvio = fields.Float(
        string='Peso a Cotizar',
        compute='_compute_peso_cotizar',
        store=True,
    )

    @api.depends("weight")
    def _compute_peso_masa(self):
        for order in self:
            order.pesoMasa = math.ceil(order.weight)

    @api.depends("width", "height", "length")
    def _compute_peso_vol(self):
        for order in self:
            order.pesoVolumetrico = math.ceil(order.width * order.height * order.length / 5000)

    @api.depends("pesoVolumetrico", "pesoMasa")
    def _compute_peso_cotizar(self):
        for order in self:
            order.pesoEnvio = math.ceil(order.pesoVolumetrico) if order.pesoVolumetrico > order.pesoMasa else math.ceil(order.pesoMasa)

    track_number = fields.Char(
        string='Número de Seguimiento',
    )
    
    track_url = fields.Char(
        string='URL de seguimiento',
    )
    
    shipping_status = fields.Char(
        string='Estado del Envío',
    )
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        domain=[],
        help='Selecciona el cliente asociado con esta orden de compra.'
    )
    
    campaign = fields.Many2one(
        'purchase.campaigns',
        string='Campaña',
        domain=[],
        help='Selecciona la Campaña relacionada a esta orden.'
    )

    campaign_product = fields.Many2many(
        'product.template',
        string='Productos de Campaña',
        domain=[],
        help='Selecciona los productos de la Campaña relacionado a esta orden.'
    )

    shipping_date = fields.Datetime(
        string='Fecha estimada de envío',
        default=fields.Datetime.now,
    )

    
    pickup = fields.Boolean(
        string='Servicio de Pickup',
    )
    
    
    pickup_customer_id = fields.Many2one(
        'res.partner',
        string='Dirección de Pickup',
        domain=[],
        help='Selecciona el cliente en cuyo dirección se realizará el pickup.'
    )

    pickup_date = fields.Datetime(
        string='Fecha estimada de Pickup',
        default=fields.Datetime.now,
    )
    
    
    
    stored_selection_options = fields.Text(
        string='Stored Selection Options',
        help='Stores the options for the selection field as a JSON string.',
    )

    def action_download_zip(self):
        
        import logging
        _logger = logging.getLogger(__name__)

        zip_buffer = io.BytesIO()
        attachments = []
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            _logger.info(f"orden de compra: {po}")
            auxAttachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'purchase.order'),
                ('res_id', '=', po.id),
                ('name', 'ilike', 'shipping_etiqueta')
            ])
            _logger.info(f"orden de compra: {auxAttachments}")

            if not auxAttachments:
                continue
            for att in auxAttachments:
                attachments.append(att)

        _logger.info(f"atts: {attachments}")
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for attachment in attachments:
                zip_file.writestr(attachment.name, base64.b64decode(attachment.datas))

        zip_buffer.seek(0)
        zip_data = base64.b64encode(zip_buffer.read())

        attachment = self.env['ir.attachment'].create({
            'name': 'archivos_pdf.zip',
            'datas': zip_data,
            'mimetype': 'application/zip',
            'res_model': 'download.zip.wizard',
            'res_id': "121",
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }


    def set_shipping_method_best(self):
        # Elegir el mejor precio entre "express domestic" y "economy select domestic"
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            methods = self.shipping_method.search([
            ("purchase_order", "=", po.id),
            ])
            
            if methods:
                best_method = min(methods, key=lambda m: m.price)
                po.shipping_method = best_method.id
                po.shipping_quote = best_method.price
        return True

    def set_shipping_method_express(self):
        
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            metodo = self.shipping_method.search([
                ("name", "ilike", "express domestic"),
                ("purchase_order", "=", po.id),
            ])
            po.shipping_method = metodo.id
            po.shipping_quote = metodo.price
        
        return True

    def set_shipping_method_economy(self):
        
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            metodo = self.shipping_method.search([
                ("name", "ilike", "economy select domestic"),
                ("purchase_order", "=", po.id),
            ])
            po.shipping_method = metodo.id
            po.shipping_quote = metodo.price
        
        return True


    def execute_request_shipping_track(self):
        orders = self.env['purchase.order'].browse(self.env.context.get("active_ids"))
        for order in orders:
            order.track()
        return True

    def execute_request_shipping_quote(self):
        orders = self.env['purchase.order'].browse(self.env.context.get("active_ids"))
        for order in orders:
            order.request_shipping_quote()
        return True

    def execute_generate_shipping_order(self):
        
        orders = self.env['purchase.order'].browse(self.env.context.get("active_ids"))
        for order in orders:
            order.generate_shipping_order()
        return True

    def button_request_shipping_quote(self):
        return super().button_request_shipping_quote()


    @api.onchange('stored_selection_options')
    def _onchange_field(self):
        if self.stored_selection_options:
            import json
            try:
                options = json.loads(self.stored_selection_options)
                
                return options
            except json.JSONDecodeError:
                return []
        return []

    def Validar(self):
        import logging
        _logger = logging.getLogger(__name__)
        if not self.partner_id: 
            # raise UserError("No has asignado Proveedor")
            _logger.warning("No has asignado Proveedor")
            self.message_post(
                body=_("No has asignado Proveedor")
            )
        if not self.customer_id: 
            # raise UserError("No has asignado Cliente")
            _logger.warning("No has asignado Cliente")
            self.message_post(
                body=_("No has asignado Cliente")
            )
        if not self.partner_id.country_code: 
            # raise UserError("El Proveedor no tiene el campo 'País' asignado correctamente")
            _logger.warning("El Proveedor no tiene el campo 'País' asignado correctamente")
            self.message_post(
                body=_("El Proveedor no tiene el campo 'País' asignado correctamente")
            )
        if not self.partner_id.city: 
            # raise UserError("El Proveedor no tiene el campo 'Ciudad' asignado correctamente")
            _logger.warning("El Proveedor no tiene el campo 'Ciudad' asignado correctamente")
            self.message_post(
                body=_("El Proveedor no tiene el campo 'Ciudad' asignado correctamente")
            )
        if not self.customer_id.country_code: 
            # raise UserError("El Cliente no tiene el campo 'País' asignado correctamente")
            _logger.warning("El Cliente no tiene el campo 'País' asignado correctamente")
            self.message_post(
                body=_("El Cliente no tiene el campo 'País' asignado correctamente")
            )
        if not self.customer_id.city: 
            # raise UserError("El Cliente no tiene el campo 'Ciudad' asignado correctamente")
            _logger.warning("El Cliente no tiene el campo 'Ciudad' asignado correctamente")
            self.message_post(
                body=_("El Cliente no tiene el campo 'Ciudad' asignado correctamente")
            )
        if not self.weight or self.weight <= 0: 
            # raise UserError("El campo 'Peso' es incorrecto")
            _logger.warning("El campo 'Peso' es incorrecto")
            self.message_post(
                body=_("El campo 'Peso' es incorrecto")
            )
        if not self.length or self.length <= 0: 
            # raise UserError("El campo 'Largo' es incorrecto")
            _logger.warning("El campo 'Largo' es incorrecto")
            self.message_post(
                body=_("El campo 'Largo' es incorrecto")
            )
        if not self.width or self.width <= 0: 
            # raise UserError("El campo 'Ancho' es incorrecto")
            _logger.warning("El campo 'Ancho' es incorrecto")
            self.message_post(
                body=_("El campo 'Ancho' es incorrecto")
            )
        if not self.height or self.height <= 0: 
            # raise UserError("El campo 'Alto' es incorrecto")
            _logger.warning("El campo 'Alto' es incorrecto")
            self.message_post(
                body=_("El campo 'Alto' es incorrecto")
            )

    def request_shipping_quote(self):
        
        from .address_info import state_code_2_digits, couriers
        import requests
        import logging
        _logger = logging.getLogger(__name__)  
        

        urlDHL = "https://express.api.dhl.com/mydhlapi/test/rates"
        urlSkydropx = "https://sb-pro.skydropx.com/"
        urlEnvia = "https://api-test.envia.com/ship/rate/"

        self.Validar()

        # date = datetime.now() + timedelta(minutes=5)
        date = self.shipping_date

        _logger.info(f"fecha formato {date.strftime('%Y-%m-%d')}")

        paramsDHL = {
            "accountNumber" : "983441463",
            "originCountryCode": self.partner_id.country_code or "MX",
            "originCityName": self.partner_id.city,
            "destinationCountryCode": self.customer_id.country_code or "MX",
            "destinationCityName" : self.customer_id.city,
            "weight": self.weight,
            "length" : self.length,
            "width" : self.width,
            "height" : self.height,
            "plannedShippingDate" : date.strftime('%Y-%m-%d'),
            "isCustomsDeclarable" : False,
            "unitOfMeasurement" : "metric",
        }

        paramsSkydropx = {
            "quotation": {
            "order_id": str(self.id),
            "address_from": {
                "country_code": self.partner_id.country_code.lower(),
                "postal_code": self.partner_id.zip,
                "area_level1": self.partner_id.state_id.name,
                "area_level2": self.partner_id.city,
                "area_level3": self.partner_id.street2 or "",
                "street1": self.partner_id.street,
                "apartment_number": "",
                "reference": "Nave 7",
                "name": ''.join(filter(str.isalpha, self.partner_id.name)),
                "company": self.partner_id.company_id.name or "",
                "phone": self.partner_id.phone or "",
                "email": self.partner_id.email or ""
            },
            "address_to": {
                "country_code": self.customer_id.country_code.lower(),
                "postal_code": self.customer_id.zip,
                "area_level1": self.customer_id.state_id.name,
                "area_level2": self.customer_id.city,
                "area_level3": self.customer_id.street2 or "",
                "street1": self.customer_id.street,
                "apartment_number": "",
                "reference": "Zaguan blanco",
                "name": ''.join(filter(str.isalpha, self.customer_id.name)),
                "company": self.customer_id.company_id.name or "",
                "phone": self.customer_id.phone or "",
                "email": self.customer_id.email or ""
            },
            "parcel": {
                "length": self.length,
                "width": self.width,
                "height": self.height,
                "weight": self.weight
            },
            "requested_carriers": [
                "all"
            ]
            }
        }

        paramsEnvia = {
            "origin": {
            "name": self.partner_id.name or '',
            "company": self.partner_id.company_id.name or '',
            "email": self.partner_id.email or '',
            "phone": self.partner_id.phone or '',
            "street": self.partner_id.street or '',
            "number": self.partner_id.street2 or '',
            "district": self.partner_id.city or '',
            "city": self.partner_id.city or '',
            "state": state_code_2_digits(self.partner_id.state_id.name) or '',
            "country": self.partner_id.country_code or '',
            "postalCode": self.partner_id.zip or '',
            "reference": "",
            },
            "destination": {
            "name": self.customer_id.name or '',
            "company": self.customer_id.company_id.name or '',
            "email": self.customer_id.email or '',
            "phone": self.customer_id.phone or '',
            "street": self.customer_id.street or '',
            "number": self.customer_id.street2 or '',
            "district": self.customer_id.city or '',
            "city": self.customer_id.city or '',
            "state": state_code_2_digits(self.customer_id.state_id.name) or '',
            "country": self.customer_id.country_code or '',
            "postalCode": self.customer_id.zip or '',
            "reference": "",
            },
            "packages": [{
            "content": ', '.join(self.campaign_product.mapped('name')) or '',
            "amount": 1,
            "type": "box",
            "weight": self.weight or 0,
            "insurance": 0,
            "declaredValue": 0,
            "weightUnit": "KG",
            "lengthUnit": "CM",
            "dimensions": {
                "length": self.length or 0,
                "width": self.width or 0,
                "height": self.height or 0
            }
            }],
            "settings": {
            "printFormat": "PDF",
            "printSize": "STOCK_4X6",
            "currency": "MXN",
            "cashOnDelivery": "0.00",
            "comments": ""
            }
        }

        # _logger.info(f"paramsEnvia: {paramsEnvia}")
        
        headersDHL = {
            'Content-Type': 'application/json',
        }
        
        headers = {
            'Content-Type': 'application/json',
        }

        # Buscar en shipping_methods si ya existe una cotización para este origen y destino no mayor a 8 horas
        self.env['shipping.methods'].search([('purchase_order', '=', self.id)]).unlink()
        existe = self.env['shipping.methods'].search([
            ('origin', '=', self.partner_id.city),
            ('destination', '=', self.customer_id.city),
            ('weight', '=', self.pesoEnvio),
            ('requestDate', '>=', datetime.now() - timedelta(hours=8)),
        ], order='purchase_order.id asc')

        # si existe, clonar los campos y cambiar la orden de compra a esta
        # if existe:
        if existe:
            _logger.info(f"existe: {existe}, en la ciudad {self.partner_id.city} a la ciudad {self.customer_id.city}")
            primera = 0
            for metodo in existe:
                if primera == 0:
                    primera = metodo.purchase_order.id
                elif primera != metodo.purchase_order.id:
                    break
                # clonar cada metodo cambiando la orden de compra
                self.env['shipping.methods'].create({
                    'name': metodo.name,
                    'shipping_code': metodo.shipping_code,
                    'price': metodo.price,
                    'purchase_order': self.id,
                    'basePrice': metodo.basePrice,
                    'discount': metodo.discount,
                    'tax': metodo.tax,
                    'fuelSurcharge': metodo.fuelSurcharge,
                    'remoteArea': metodo.remoteArea,
                    'requestDate': datetime.now(),
                    'weight': metodo.weight,
                    'origin': metodo.origin,
                    'courier': metodo.courier,
                    'destination': metodo.destination,
                    'processedBy': metodo.processedBy,
                    'peakSeason': metodo.peakSeason,
                })
            self.shipping_method = self.env['shipping.methods'].search([('purchase_order', '=', self.id)], limit=1)

            self.shipping_quote = self.shipping_method.price
            self.message_post(
            body=_(f"Se ha obtenido la cotización del envio: {self.shipping_quote}"),
            )
        # si no existe, hacer la solicitud a DHL y guardar los datos en shipping_methods
        else:
            # _logger.info(f"no existe, llamar api")
            tiempo = datetime.now()
            try:
                async def fetch(session, url, params, headers, handler, courier):
                    if handler == 'Skydropx':
                        token = self.env['ir.config_parameter'].sudo().get_param('skydropx_token')

                        if token:
                            token_data = json.loads(token)
                            if 'expires_in' in token_data and token_data['expires_in'] < datetime.now().timestamp():
                                token = None
                        if not token:
                            # Solicitar un nuevo token a Skydropx
                            auth_response = await session.post(
                                urlSkydropx + 'api/v1/oauth/token',
                                json={
                                    "grant_type": "client_credentials",
                                    "client_id" : "KRJ2ZCd6dxBNPCBKeIxmYfJ25_VU-Z8ULVudhct3MKI",
                                    "client_secret" : "xYP0CsERedn2I_MWXnY3pOaPbjP4ty2o38WHkSEUYq4"
                                },
                                headers=headers
                            )
                            
                            token = await auth_response.json()
                            if token:
                                self.env['ir.config_parameter'].sudo().set_param('skydropx_token', json.dumps(token))
                            else:
                                _logger.warning('No se pudo obtener el token de Skydropx')
                        _logger.info(f"token: {token}")
                        headers['Authorization'] = f'Bearer {token["access_token"]}'
                        async with session.post(url, json=params, headers=headers) as response:
                            _logger.info(f"response: {response}")
                            respuesta = await response.json()
                            _logger.info(f"respuesta: {respuesta}")

                            if 'error' in respuesta or ('code' in respuesta and (respuesta["code"] == 500 or respuesta["code"] == 400)) or ("data" in respuesta and isinstance(respuesta["data"], str)):
                                return

                            quote_id = respuesta.get('id')
                            if not quote_id:
                                _logger.warning('No se pudo obtener el ID de la cotización.')
                                return

                            while True:
                                async with session.get(f"{url}/{quote_id}", headers=headers) as check_response:
                                    check_respuesta = await check_response.json()
                                    _logger.info(f"check_respuesta: {check_respuesta}")

                                    if check_respuesta.get('is_completed'):
                                        products = check_respuesta['rates']
                                        if not products:
                                            _logger.warning('No se encontraron métodos de envío disponibles.')
                                            return

                                        for product in products:
                                            if product["success"]:
                                                tax = 0
                                                aux = {
                                                    'name': product['provider_name'] + " " + product["provider_service_name"] + " - " + f"${float(product['total']):,.2f}",
                                                    'rate_id': product['id'],
                                                    'shipping_code': product['provider_service_code'],
                                                    'price': product['total'],
                                                    'purchase_order': self.id,
                                                    'courier': product['provider_name'],
                                                    'weight': self.pesoEnvio,
                                                    'origin': self.partner_id.city,
                                                    'destination': self.customer_id.city,
                                                    'requestDate': datetime.now(),
                                                    'other': 0,
                                                    'processedBy': handler
                                                }
                                                descuentoAdicional = 0

                                                aux["basePrice"] = float(product["amount"]) / 1.16
                                                tax = aux["basePrice"]*.16

                                                for additional in product["extra_fees"]:
                                                    if additional["code"] == "FUEL_SURCHARGE_FEE":
                                                        aux["fuelSurcharge"] = additional["value"]/1.16
                                                        tax += aux["fuelSurcharge"]*.16
                                                    elif "additionalService" in additional:
                                                        if additional["additionalService"] == "PEAK_SEASON_FEE":
                                                            aux["peakSeason"] = additional["value"]/1.16
                                                            tax += aux["peakSeason"]*.16
                                                        elif additional["additionalService"] == "REMOTE_AREA_FEE":
                                                            aux["remoteArea"] = additional["value"]/1.16
                                                            tax += aux["remoteArea"]*.16
                                                    else:
                                                        aux["other"] += additional["value"]/1.16
                                                        tax += aux["other"]*.16
                                                aux["tax"] = tax
                                                self.env['shipping.methods'].create(aux)
                                                self.env.cr.commit()

                                        self.shipping_method = self.env['shipping.methods'].search([('purchase_order', '=', self.id)], limit=1)
                                        self.shipping_quote = self.shipping_method.price
                                        break
                                    else:
                                        await asyncio.sleep(4)

                    elif handler == 'Envia':
                        
                        headers["authorization"] = "Bearer fec0e63254d3ef6053c61fe504b33acd30d27838281e2624267b1aa14ebd3c14"
                        async with session.post(url, data=params, headers=headers) as response:
                            respuesta = await response.json()
                            
                            if 'error' in respuesta or ('code' in respuesta and (respuesta["code"] == 500 or respuesta["code"] == 400)) or ("data" in respuesta and isinstance(respuesta["data"], str)):
                                # _logger.warning(f"Error en la respuesta: {respuesta}")
                                return
                            products = respuesta['data']
                            
                            if not products:
                                _logger.warning('No se encontraron métodos de envío disponibles.')

                            for product in products:
                                tax = 0
                                aux = {
                                    'name': product['serviceDescription'] + " - " + f"${product['totalPrice']:,.2f}",
                                    'shipping_code': product['service'],
                                    'price': product['totalPrice'],
                                    'purchase_order': self.id,
                                    'courier': courier,
                                    'weight': self.pesoEnvio,
                                    'origin': self.partner_id.city,
                                    'destination': self.customer_id.city,
                                    'requestDate': datetime.now(),
                                    'other': 0,
                                    'processedBy': handler
                                }
                                descuentoAdicional = 0
                                if "costSummary" in product:
                                    costSummary = product["costSummary"][0]
                                    aux["basePrice"] = costSummary["basePrice"] / 1.16
                                    tax = costSummary["basePrice"] - aux["basePrice"]
                                    
                                    for additional in costSummary["costAdditionalCharges"]:
                                        if additional["additionalService"] == "fuel":
                                            aux["fuelSurcharge"] = additional["commission"]
                                            tax += additional["taxes"]
                                        elif additional["additionalService"] == "peak_season":
                                            aux["peakSeason"] = additional["commission"]
                                            tax += additional["taxes"]
                                        else:
                                            aux["other"] += additional["commission"]
                                            tax += additional["taxes"]
                                aux["tax"] = tax
                                self.env['shipping.methods'].create(aux)
                                self.env.cr.commit()

                            self.shipping_method = self.env['shipping.methods'].search([('purchase_order', '=', self.id)], limit=1)
                            self.shipping_quote = self.shipping_method.price

                    elif handler == 'DHL':
                        async with session.get(url, params=params, headers=headers, auth=aiohttp.BasicAuth('apT3cE5nH6mP9o', 'V#2nZ^1eH$8uU$7n')) as response:
                            quote_data = await response.json()
                            
                            products = quote_data.get('products', [])
                        
                        if not products:
                            _logger.warning('No se encontraron métodos de envío disponibles.')
                            # raise UserError(_('No se encontraron métodos de envío disponibles.'))

                        for product in products:
                            if product['productName'] and product["totalPrice"][0]["price"] != 0 and product['productName'] in ['ECONOMY SELECT DOMESTIC', 'EXPRESS DOMESTIC', 'DOMESTICO ENVIO RETORNO']:
                                aux = {
                                    'name': product['productName'] + " - " + f"${product["totalPrice"][0]["price"]:,.2f}",
                                    'shipping_code': product['productCode'],
                                    'price': product["totalPrice"][0]["price"],
                                    'courier': handler,
                                    'processedBy': handler,
                                    'purchase_order': self.id,
                                    'weight': self.pesoEnvio,
                                    'origin': self.partner_id.city,
                                    'destination': self.customer_id.city,
                                    'requestDate': datetime.now(),
                                }
                                descuentoAdicional = 0
                                if "detailedPriceBreakdown" in product:
                                    # _logger.info(f"product_detail: {product["detailedPriceBreakdown"]}")
                                    if product["detailedPriceBreakdown"][0]["breakdown"][0]["price"] != 0:
                                        aux['basePrice'] = product["detailedPriceBreakdown"][0]["breakdown"][0]["priceBreakdown"][1]["basePrice"]

                                if product["totalPrice"][0]["price"] != 0 and product["detailedPriceBreakdown"]:
                                    for breakdown in product["detailedPriceBreakdown"][0]["breakdown"]:
                                        if "serviceCode" in breakdown and "price" in breakdown:
                                            if breakdown["serviceCode"] == "FF":
                                                aux['fuelSurcharge'] = breakdown["price"]/1.16
                                                descuentoAdicional += breakdown["priceBreakdown"][1]["price"]
                                            elif breakdown["serviceCode"] == "OO":
                                                aux['remoteArea'] = breakdown["price"]/1.16

                                if product["totalPrice"][0]["price"] != 0 and product["totalPriceBreakdown"]:
                                    aux['discount'] = -abs(next(item["price"] for item in product["totalPriceBreakdown"][0]["priceBreakdown"] if item["typeCode"] == "STDIS")-descuentoAdicional)
                                    aux['tax'] = next(item["price"] for item in product["totalPriceBreakdown"][0]["priceBreakdown"] if item["typeCode"] == "STTXA")
                                else:
                                    aux['discount'] = 0
                                    aux['tax'] = 0
                                precio = self.env['shipping.methods'].create(aux)
                                self.env.cr.commit()

                        # Asignar el primer método de envío como predeterminado (puedes ajustar esto)
                        self.shipping_method = self.env['shipping.methods'].search([('purchase_order', '=', self.id)], limit=1)

                        metodos = [
                            (product['productCode'], f"{product['productName']} - {product["totalPrice"][0]["price"]}")
                            for product in products
                        ]


                        # _logger.info(f"metodos: {metodos}")
                        
                        self.stored_selection_options = json.dumps(metodos)
                        
                        self.shipping_quote = self.shipping_method.price

                async def fetch_all():
                    async with aiohttp.ClientSession() as session:
                        tasks = []

                        # DHL
                        tasks.append(fetch(session, urlDHL, paramsDHL, headersDHL, "DHL", "DHL"))

                        # obtener el token guardado localmente
                        # si no existe el token solicitad uno a skydropx
                        # si existe el token, solicitar cotización a skydropx
                        
                        # Skydropx
                        tasks.append(fetch(session, urlSkydropx+"api/v1/quotations", paramsSkydropx, headers, "Skydropx", "Skydropx"))
                        
                        # Envia
                        for courier in couriers:
                            paramsEnvia['shipment'] = {
                                "carrier": courier,
                                "type": 0
                            }
                            _logger.info(f"Paquetería: {courier}")
                            tasks.append(fetch(session, urlEnvia, json.dumps(paramsEnvia), headers, "Envia", courier))
                        await asyncio.gather(*tasks)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(fetch_all())
            except Exception as e:
                _logger.error(f"Error fetching shipping quotes: {e}")
                self.message_post(
                    body=_(f"Error fetching shipping quotes: {e}"),
                )
                return
            
    def generate_shipping_order(self):

        # obtener tipo de envio:

        metodo = self.shipping_method
    
        if metodo.processedBy == 'Envia':
            self.get_guide_Envia(metodo)
        elif metodo.processedBy == 'Skydropx':
            self.get_guide_Skydropx(metodo)
        else:
            self.get_guide_DHL(metodo)

            
    def get_guide_Envia(self, metodo):
        import logging
        from .address_info import state_code_2_digits
        _logger = logging.getLogger(__name__)  

        self.shipping_quote = metodo.price
        
        
        date = datetime.now() + timedelta(minutes=5)
        formatted_dt = date.strftime("%Y-%m-%dT%H:%M:%S GMT-06:00")
        _logger.info(f"fecha formato {formatted_dt}")

        paramsEnvia = {
            "origin": {
                "name": self.partner_id.name or '',
                "company": self.partner_id.company_id.name or '',
                "email": self.partner_id.email or '',
                "phone": self.partner_id.phone or '',
                "street": self.partner_id.street or '',
                "number": self.partner_id.street2 or '',
                "district": self.partner_id.city or '',
                "city": self.partner_id.city or '',
                "state": state_code_2_digits(self.partner_id.state_id.name) or '',
                "country": self.partner_id.country_code or '',
                "postalCode": self.partner_id.zip or '',
                "reference": "",
            },
            "destination": {
                "name": self.customer_id.name or '',
                "company": self.customer_id.company_id.name or '',
                "email": self.customer_id.email or '',
                "phone": self.customer_id.phone or '',
                "street": self.customer_id.street or '',
                "number": self.customer_id.street2 or '',
                "district": self.customer_id.city or '',
                "city": self.customer_id.city or '',
                "state": state_code_2_digits(self.customer_id.state_id.name) or '',
                "country": self.customer_id.country_code or '',
                "postalCode": self.customer_id.zip or '',
                "reference": "",
            },
            "packages": [{
                "content": ', '.join(self.campaign_product.mapped('name')) or '',
                "amount": 1,
                "type": "box",
                "weight": self.weight or 0,
                "insurance": 0,
                "declaredValue": 0,
                "weightUnit": "KG",
                "lengthUnit": "CM",
                "dimensions": {
                    "length": self.length or 0,
                    "width": self.width or 0,
                    "height": self.height or 0
                }
            }],
            "shipment": {
                "carrier": metodo.courier,
                "service": metodo.shipping_code,
                "type": 0
            },
            "settings": {
                "printFormat": "PDF",
                "printSize": "STOCK_4X6",
                "currency": "MXN",
                "cashOnDelivery": "0.00",
                "comments": ""
            }
        }

        # paramsEnvia = paramsEnvia.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        
        headers = {
            'Content-Type': 'application/json',
            'authorization': "Bearer fec0e63254d3ef6053c61fe504b33acd30d27838281e2624267b1aa14ebd3c14"
        }

        try:
            _logger.info(f"paramsEnvia: {paramsEnvia}")
            response = requests.post(
                'https://api-test.envia.com/ship/generate/',
                headers=headers,
                json=paramsEnvia
            )
            _logger.info(f"response: {response}")
            if response.status_code == 200:
                
                resp = response.json()
                if 'error' in resp:
                    raise UserError(_('No se pudo generar la orden 1: %s') % resp['error'])
                else:
                    data = resp['data'][0]

                    self.track_number = data['trackingNumber']
                    self.track_url = data['trackUrl']
                    self.shipping_status = 'Guía Creada'
                    
                    # obtener el PDF desde aws con el campo "label" y crear un archivo
                    urlLabel = data['label']
                    response = requests.get(urlLabel)
                    pdf_content = response.content
                    if not pdf_content:
                        raise UserError(_('No se pudo obtener la etiqueta de envío'))

                    # Adjuntar el PDF directamente al chatter
                    attachment = self.env['ir.attachment'].create({
                        'name': f'shipping_etiqueta_{self.name}.pdf',
                        'type': 'binary',
                        'datas': base64.b64encode(pdf_content),
                        'res_model': 'purchase.order',
                        'res_id': self.id,
                        'mimetype': 'application/pdf',
                    })
                    # Agregar el adjunto al chatter

                    envio = self.env['product.product'].search([
                        ('name', '=', 'Envío')
                    ])

                    existe = self.order_line.filtered(lambda line: line.product_id == envio)

                    if existe: 
                        existe.write({
                            'price_unit': metodo.price,  # Actualizar el precio
                            'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                        })

                    else:
                        self.order_line.create({
                            'order_id': self.id,  # Asociar la línea a esta orden de compra
                            'product_id': envio.id,  # Producto "Envío"
                            'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                            'product_qty': 1.0,  # Cantidad
                            'product_uom': envio.uom_id.id,  # Unidad de medida
                            'price_unit': metodo.price,  # Precio del envío
                        })


                    self.message_post(
                        body=_("Se ha generado la orden de envío y se ha adjuntado la etiqueta."),
                        attachment_ids=[attachment.id]
                    )
            else:
                _logger.warning(f"No se pudo generar la orden: {response.text()}")
                # raise UserError(_('No se pudo generar la orden: %s') % response
        except Exception as e:
            raise UserError(_('No se pudo generar la orden: %s') % str(e))
        
        
    def get_guide_Skydropx(self, metodo):
        import logging
        from .address_info import state_code_2_digits
        _logger = logging.getLogger(__name__)  

        self.shipping_quote = metodo.price
        
        
        urlSkydropx = "https://sb-pro.skydropx.com/"
        date = datetime.now() + timedelta(minutes=5)
        formatted_dt = date.strftime("%Y-%m-%dT%H:%M:%S GMT-06:00")
        _logger.info(f"fecha formato {formatted_dt}")

        paramsSkydropx = {
            "shipment": {
            "rate_id": metodo.rate_id,
            "protected": True,
            "declared_value": 1400,
            "printing_format": "thermal",
            "address_from": {
                "country_code": self.partner_id.country_code.lower(),
                "postal_code": self.partner_id.zip,
                "area_level1": self.partner_id.state_id.name,
                "area_level2": self.partner_id.city,
                "area_level3": self.partner_id.street2 or "",
                "street1": self.partner_id.street,
                "name": ''.join(filter(str.isalpha, self.partner_id.name)),
                "company": self.partner_id.company_id.name or "",
                "phone": self.partner_id.phone or "",
                "email": self.partner_id.email or "",
                "reference": self.partner_id.street2 or ""
            },
            "address_to": {
                "country_code": self.customer_id.country_code.lower(),
                "postal_code": self.customer_id.zip,
                "area_level1": self.customer_id.state_id.name,
                "area_level2": self.customer_id.city,
                "area_level3": self.customer_id.street2 or "",
                "street1": self.customer_id.street,
                "name": ''.join(filter(str.isalpha, self.customer_id.name)),
                "company": self.customer_id.company_id.name or "",
                "phone": self.customer_id.phone or "",
                "email": self.customer_id.email or "",
                "reference": self.customer_id.street2 or ""
            },
            "consignment_note": '53102400',
            "package_type": "4G",
            "products": []
            }
        }

        # paramsEnvia = paramsEnvia.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            async def fetch(session, url, params, headers, handler, courier):
                if handler == 'Skydropx':
                    async with session.post(url, json=params, headers=headers) as response:
                        resp = await response.json()
                        _logger.info(f"resp: {resp}")

                        if 'error' in resp:
                            raise UserError(_('No se pudo generar la orden 1: %s') % resp['error'])
                        else:
                            id = resp['data']["id"]
                            while True:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(urlSkydropx + 'api/v1/shipments/' + str(id), headers=headers) as response:
                                        resp = await response.json()
                                        # _logger.info(f"Checking shipment status: {resp}")

                                        if resp["data"]["attributes"]["workflow_status"] == "success":
                                            data = resp
                                            self.track_number = data['included'][0]["attributes"]["tracking_number"]
                                            self.track_url = data['included'][0]["attributes"]["tracking_url_provider"]
                                            self.shipping_status = 'Guía Creada'
                                            
                                            # obtener el PDF desde aws con el campo "label" y crear un archivo
                                            urlLabel = urlSkydropx.rstrip('/') + data['included'][0]["attributes"]["label_url"]

                                            _logger.info(f"url del pdf {urlLabel}")
                                            """
                                            login_url = "https://sb-pro.skydropx.com/es-MX/users/sign_in"
                                            credentials = {
                                                "user": {
                                                    "email": "champy.cruz@gmail.com",
                                                    "password": "Siddhartha21."
                                                }
                                            }

                                            # Iniciar sesión y guardar cookies
                                            session = requests.Session()
                                            login_response = session.post(login_url, json=credentials)

                                            if login_response.status_code == 200:
                                                _logger.info("Inicio de sesión exitoso")

                                            cookies = session.cookies.get_dict()
                                            _logger.info(f"Cookies después del login: {cookies}")
                                            """
                                            # Enviar la solicitud con las cookies manualmente
                                            """
                                                _vid_t=qhWGY+HBm5l+5q5M4qU7BuvQ6gUo2Gvfr4uWwmSlHh/enwkh42v9Bv0rjU+dMfqCuoIOn8jM1tXMDrqvgGx2x4uLZiXb1rjAcmC2psM=; _ll_hub_session_staging=94298f9d1ae0c70a190ee517942bae6c; locale=es-MX; cf_clearance=tJG4j0KBgC8FNuO1yDRg.UTgwP80wLKnX3SsLlmksHo-1739300523-1.2.1.1-LsSiyY.4qHfj3ihmg.ctY9Xe1tbdsSAUXRTaxsPyEVpbRu1Cog9h7X_YSAPMCeeyKs6PsWhjy2PukYDBY9MyrXad4WxeTqxITJImF3ysPEKM3wQUoolR4GbyLrKPCgzvlU2kiK5i9w5fQ47z0vs2P8kqbd5UwK1FDexqCEpVkIBwKdnDKhKMyBSsIXi4IIdqE9Fx64UxN.9chvjRpVkoHDvNDxNezlIjzBV0Wk48J5C_rNkyXPvAslP6xO62P179kJ0_E76P5CQbWE2TTlTwe9OXIG4fLdbRkhGg5CR1qT0
                                            """
                                            headers = {
                                                "Cookie": f"_vid_t=qhWGY+HBm5l+5q5M4qU7BuvQ6gUo2Gvfr4uWwmSlHh/enwkh42v9Bv0rjU+dMfqCuoIOn8jM1tXMDrqvgGx2x4uLZiXb1rjAcmC2psM=; _ll_hub_session_staging=94298f9d1ae0c70a190ee517942bae6c; locale=es-MX; cf_clearance=6gS.LXToZq5JIRq5I54WMM35SwcIgVG2o3Gkc5ASUBw-1739343295-1.2.1.1-FGNJGcskc_CxWuD9XiF0lFp888wxt4NhPIsiKW7hJr5.DI5zNZjdSSiQzE7kCgp7EjLmgnYJFvljQ5xT3a0sAmAITW3AaoPv3lRSfzdQZzwLRbLFnVz8awX09MjO0zRacl_Xqa_JgZNsCvcsRaHOe6wPdN37uvd72kmAhZN.zhzKZdLo_Ru8X8cZP8TjsRD8XlMHGWU8FQ7C5CIdaWit8O9g_6eQxnRAKWO2Ezjs6su6Ypc52fbXVAthYH4KMNHxm7nlfqUZ3NxKOl3vFz0I6pfnqXHjHfpU3gBHX9bF9A8",
                                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
                                            }

                                            _logger.info(f"encabezado: {headers}")

                                            async with session.get(urlLabel, headers=headers) as response:
                                                _logger.info(f"response: {response}")

                                                if response.status == 200:
                                                    pdf_content = await response.read()
                                                    _logger.info("Etiqueta descargada correctamente")
                                                else:
                                                    _logger.info(f"Error en la descarga: {response.status} - {await response.text()}")

                                                if not pdf_content:
                                                    _logger.warning('No se pudo obtener la etiqueta de envío')
                                                _logger.info(f"contenido del pdf:{pdf_content}")
                                                # Adjuntar el PDF directamente al chatter
                                                attachment = self.env['ir.attachment'].create({
                                                    'name': f'shipping_etiqueta_{self.name}.pdf',
                                                    'type': 'binary',
                                                    'datas': base64.b64encode(pdf_content),
                                                    'res_model': 'purchase.order',
                                                    'res_id': self.id,
                                                    'mimetype': 'application/pdf',
                                                })
                                                # Agregar el adjunto al chatter

                                                envio = self.env['product.product'].search([
                                                    ('name', '=', 'Envío')
                                                ])

                                                existe = self.order_line.filtered(lambda line: line.product_id == envio)

                                                if existe: 
                                                    existe.write({
                                                        'price_unit': metodo.price,  # Actualizar el precio
                                                        'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                                                    })

                                                else:
                                                    self.order_line.create({
                                                        'order_id': self.id,  # Asociar la línea a esta orden de compra
                                                        'product_id': envio.id,  # Producto "Envío"
                                                        'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                                                        'product_qty': 1.0,  # Cantidad
                                                        'product_uom': envio.uom_id.id,  # Unidad de medida
                                                        'price_unit': metodo.price,  # Precio del envío
                                                    })


                                                self.message_post(
                                                    body=_("Se ha generado la orden de envío y se ha adjuntado la etiqueta."),
                                                    attachment_ids=[attachment.id]
                                                )
                                                break

                                        await asyncio.sleep(5)
                    

            async def fetch_all():
                async with aiohttp.ClientSession() as session:
                    tasks = []

                    token = self.env['ir.config_parameter'].sudo().get_param('skydropx_token')

                    if token:
                        token_data = json.loads(token)
                        if 'expires_in' in token_data and token_data['expires_in'] < datetime.now().timestamp():
                            token = None
                    if not token:
                        # Solicitar un nuevo token a Skydropx
                        auth_response = await session.post(
                            urlSkydropx + 'api/v1/oauth/token',
                            json={
                                "grant_type": "client_credentials",
                                "client_id" : "KRJ2ZCd6dxBNPCBKeIxmYfJ25_VU-Z8ULVudhct3MKI",
                                "client_secret" : "xYP0CsERedn2I_MWXnY3pOaPbjP4ty2o38WHkSEUYq4"
                            },
                            headers=headers
                        )
                        
                        token = await auth_response.json()
                        if token:
                            self.env['ir.config_parameter'].sudo().set_param('skydropx_token', json.dumps(token))
                        else:
                            _logger.warning('No se pudo obtener el token de Skydropx')
                    _logger.info(f"token: {token}")
                    headers['Authorization'] = f'Bearer {token["access_token"]}'

                    tasks.append(fetch(session, urlSkydropx+"api/v1/shipments", paramsSkydropx, headers, "Skydropx", "Skydropx"))
                    await asyncio.gather(*tasks)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_all())
        except Exception as e:
            raise UserError(_('No se pudo generar la orden: %s') % str(e))
        

    def get_guide_DHL(self, metodo):
        self.shipping_quote = metodo.price
        
        import logging
        _logger = logging.getLogger(__name__)        
        
        date = datetime.now() + timedelta(minutes=5)
        formatted_dt = date.strftime("%Y-%m-%dT%H:%M:%S GMT-06:00")
        _logger.info(f"fecha formato {formatted_dt}")

        payload = {
            "plannedShippingDateAndTime": formatted_dt,
            "productCode": metodo.shipping_code,
            "getRateEstimates": False,
            "accounts": [
                {
                    "number": "983441463",
                    "typeCode": "shipper"
                }
            ],
            "pickup": {
                "isRequested" : self.pickup,
                # "pickupDetails" : {
                #     "postalAddress": {
                #         "postalCode": self.pickup_customer_id.zip,
                #         "cityName": self.pickup_customer_id.city,
                #         "countryCode": self.pickup_customer_id.fiscal_country_codes or "MX",
                #         "addressLine1": self.pickup_customer_id.street_name,
                #         "addressLine1": self.pickup_customer_id.street_number + " " + self.pickup_customer_id.street_number2,
                #     },
                #     "contactInformation": {
                #         "email": self.pickup_customer_id.email or "shipper_create_shipmentapi@dhltestmail.com",
                #         "phone": self.pickup_customer_id.phone or "5523088355",
                #         "companyName": self.pickup_customer_id.company_id.name or "DPR Wholesalers",
                #         "fullName": self.pickup_customer_id.name
                #     },
                # }
            },
            "outputImageProperties": {
                "printerDPI": 300,
                "encodingFormat": "pdf",
                "imageOptions": [
                {
                    "typeCode": "waybillDoc",
                    "templateName": "ARCH_8x4",
                    "isRequested": True,
                    "hideAccountNumber": True,
                    "numberOfCopies": 1
                },
                {
                    "typeCode": "label",
                    "templateName": "ECOM26_84_001",
                    "isRequested": True
                }
                ],
                "splitTransportAndWaybillDocLabels": True,
                "allDocumentsInOneImage": False,
                "splitDocumentsByPages": True,
                "splitInvoiceAndReceipt": True,
                "receiptAndLabelsInOneImage": False
            },
            "customerDetails": {
                "shipperDetails": {
                    "postalAddress": {
                        "postalCode": self.partner_id.zip,
                        "cityName": self.partner_id.city,
                        "countryCode": self.partner_id.country_code or "MX",
                        "addressLine1": self.partner_id.street,
                        "addressLine2": self.partner_id.street2,
                    },
                    "contactInformation": {
                        "email": self.partner_id.email or "shipper_create_shipmentapi@dhltestmail.com",
                        "phone": self.partner_id.phone or "5523088355",
                        "companyName": self.partner_id.company_id.name or "DPR Wholesalers",
                        "fullName": self.partner_id.name
                    },
                    "registrationNumbers": [
                        {
                        "typeCode": "VAT",
                        "number": "244444911",
                        "issuerCountryCode": self.partner_id.country_code or "MX"
                        }
                    ],
                    "typeCode": "business"
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": self.customer_id.zip,
                        "cityName": self.customer_id.city,
                        "countryCode": self.customer_id.country_code or "MX",
                        "addressLine1": self.customer_id.street,
                        "addressLine2": self.customer_id.street2,
                    },
                    "contactInformation": {
                        "email": self.customer_id.email or "recipient_create_shipmentapi@dhltestmail.com",
                        "phone": self.customer_id.phone or "5523088355",
                        "companyName": self.customer_id.company_id.name or "DPR Wholesalers",
                        "fullName": self.customer_id.name
                    },
                    "registrationNumbers": [
                        {
                        "typeCode": "VAT",
                        "number": "12345678",
                        "issuerCountryCode": self.customer_id.country_code or "MX"
                        }
                    ],
                    "typeCode": "business"
                }
            },
            "content": {
                "packages": [
                {
                    "typeCode": "2BP",
                    "weight": self.pesoEnvio,
                    "dimensions": {
                        "length": self.length,
                        "width": self.width,
                        "height": self.height
                    }
                }
                ],
                "isCustomsDeclarable": False,
                "description": "Shipment Description",
                "incoterm": "DAP",
                "unitOfMeasurement": "metric"
            },
            "getTransliteratedResponse": False,
        }

        
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                'https://express.api.dhl.com/mydhlapi/test/shipments',
                auth=('apT3cE5nH6mP9o', 'V#2nZ^1eH$8uU$7n'),
                headers=headers,
                data=json.dumps(payload)
            )
            import logging
            if response.status_code == 201:
                # Procesar la respuesta y obtener el PDF de la etiqueta
                data = response.json()

                self.track_number = data['shipmentTrackingNumber']
                self.track_url = data['trackingUrl']
                self.shipping_status = 'Guía Creada'
                
                pdf_content = data["documents"][0]["content"]
                if not pdf_content:
                    raise UserError(_('No se pudo obtener la etiqueta de envío'))

                # Decodificar el PDF (base64) y adjuntarlo al chatter
                pdf_data = base64.b64decode(pdf_content)
                attachment = self.env['ir.attachment'].create({
                    'name': f'shipping_etiqueta_{self.name}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_data),
                    'res_model': 'purchase.order',
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                # Agregar el adjunto al chatter

                envio = self.env['product.product'].search([
                    ('name', '=', 'Envío')
                ])

                existe = self.order_line.filtered(lambda line: line.product_id == envio)

                if existe: 
                    existe.write({
                        'price_unit': metodo.price,  # Actualizar el precio
                        'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                    })

                else:
                    self.order_line.create({
                        'order_id': self.id,  # Asociar la línea a esta orden de compra
                        'product_id': envio.id,  # Producto "Envío"
                        'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                        'product_qty': 1.0,  # Cantidad
                        'product_uom': envio.uom_id.id,  # Unidad de medida
                        'price_unit': metodo.price,  # Precio del envío
                    })


                self.message_post(
                    body=_("Se ha generado la orden de envío y se ha adjuntado la etiqueta."),
                    attachment_ids=[attachment.id]
                )
            else:
                raise UserError(_('Error al generar la orden: %s') % response.text)
        except Exception as e:
            raise UserError(_('No se pudo generar la orden: %s') % str(e))
        
    def track(self):

        import requests
        import logging
        _logger = logging.getLogger(__name__)  
        

        urlDHL = "https://express.api.dhl.com/mydhlapi/test/shipments/" + self.track_number + "/tracking"
        
        headers = {
            'Content-Type': 'application/json',
        }

        classification = {
            "Registrados": ['PY', 'SD', 'SM', 'MF'],
            "Recolectados": ['PU', 'SA'],
            "En tránsito": ['AF', 'AR', 'DF', 'EM', 'FD', 'LV', 'PL', 'TI', 'TP', 'UV', 'IC'],
            "Entrega en proceso": ['CC', 'WC'],
            "Entregados": ['OK', 'AD', 'DD', 'PD', 'TR'],
            "Incidencias": ['BA', 'CA', 'CD', 'CR', 'DM', 'DP', 'DS', 'HN', 'HP', 'MC', 'MD', 'MS', 'NA', 'ND', 'NH', 'RD', 'RT', 'SC', 'SI', 'SS', 'ST', 'TD', 'TT', 'UD'],
            "Cancelados": ['CS', 'HI', 'HO'],
            "Devueltos": ['BN', 'BR', 'CM']
        }

        try:



            response = requests.get(
                urlDHL,
                auth=('apT3cE5nH6mP9o', 'V#2nZ^1eH$8uU$7n'),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()

                _logger.info(data)
                # self.shipping_status = data['shipments'][0]['estimatedDeliveryDate']
                self.env['shipping.events'].search([('purchase_order', '=', self.id)]).unlink()
                events = data.get('events', [])
                if not events:
                    events = [
                        {
                            "date": "2023-08-09",
                            "time": "13:56:21",
                            "typeCode": "PU",
                            "description": "Shipment picked up",
                            "serviceArea": [
                                {
                                    "code": "SYD",
                                    "description": "SYDNEY-AU"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-09",
                            "time": "18:47:01",
                            "typeCode": "AF",
                            "description": "Arrived at DHL Sort Facility - SYDNEY-AU",
                            "serviceArea": [
                                {
                                    "code": "SYD",
                                    "description": "SYDNEY-AU"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-09",
                            "time": "19:40:02",
                            "typeCode": "PL",
                            "description": "Processed at- SYDNEY-AU",
                            "serviceArea": [
                                {
                                    "code": "SYD",
                                    "description": "SYDNEY-AU"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-09",
                            "time": "21:28:58",
                            "typeCode": "DF",
                            "description": "Shipment has departed from a DHL facility- SYDNEY-AU",
                            "serviceArea": [
                                {
                                    "code": "SYD",
                                    "description": "SYDNEY-AU"
                                }
                            ],
                            "remarks": [
                                {
                                    "value": "The shipment is on its way to the destination.",
                                    "details": "Please continue to monitor the progress online. If you are the consignee and would like to change your delivery preference, please visit https://delivery.dhl.com."
                                }
                            ]
                        },
                        {
                            "date": "2023-08-09",
                            "time": "21:49:12",
                            "typeCode": "RR",
                            "description": "Customs clearance status updated. Note - The Customs clearance process may start while the shipment is in transit to the destination. ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-09",
                            "time": "22:35:34",
                            "typeCode": "RR",
                            "description": "Customs clearance status updated. Note - The Customs clearance process may start while the shipment is in transit to the destination. ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ],
                            "remarks": [
                                {
                                    "value": "Shipment has been given a release status by Customs.",
                                    "details": "Unless there is an adhoc physical examination or a stop by another regulatory authority the shipment will proceed to DHL delivery facility. Please continue to monitor the progress online."
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "04:09:01",
                            "typeCode": "AF",
                            "description": "Arrived at DHL Sort Facility - AUCKLAND-NZ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "04:18:00",
                            "typeCode": "CR",
                            "description": "Clearance processing complete at- AUCKLAND-NZ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "05:58:15",
                            "typeCode": "PL",
                            "description": "Processed at- AUCKLAND-NZ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "05:58:58",
                            "typeCode": "DF",
                            "description": "Shipment has departed from a DHL facility- AUCKLAND-NZ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ],
                            "remarks": [
                                {
                                    "value": "The shipment is on its way to the destination.",
                                    "details": "Please continue to monitor the progress online. If you are the consignee and would like to change your delivery preference, please visit https://delivery.dhl.com."
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "09:50:00",
                            "typeCode": "AR",
                            "description": "Arrived at DHL Delivery Facility - AUCKLAND-NZ",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ]
                        },
                        {
                            "date": "2023-08-10",
                            "time": "10:50:14",
                            "typeCode": "WC",
                            "description": "Shipment is out with courier for delivery",
                            "serviceArea": [
                                {
                                    "code": "AKL",
                                    "description": "AUCKLAND-NZ"
                                }
                            ],
                            "remarks": [
                                {
                                    "value": "Shipment is taken out for delivery",
                                    "details": "Expect delivery today"
                                }
                            ]
                        },
                    ]
                for event in events:
                    self.env['shipping.events'].create({
                        'purchase_order': self.id,
                        'track_number': self.track_number,
                        'name': event['description'],
                        'date': event['date'],
                        'time': event['time'],
                        'code': event['typeCode'],
                    })
                if events:
                    most_recent_event = max(
                        events,
                        key=lambda e: datetime.strptime(f"{e['date']} {e['time']}", "%Y-%m-%d %H:%M:%S")
                    )

                    # Obtener el código del evento más reciente
                    most_recent_code = most_recent_event["typeCode"]
                    classification_found = next(
                        (state for state, codes in classification.items() if most_recent_code in codes),
                        None
                    )

                    self.shipping_status = classification_found
                else:
                    self.shipping_status = 'Registrado'
                    

            else:
                raise Exception(_('Error en la solicitud de tracking: %s \n %s') % (response.text, response.status_code))
        except Exception as e:
            raise models.UserError(_('No se pudo obtener el estado: %s') % str(e))
