from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import base64
import math

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

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
    
    dhl_quote = fields.Float(string='DHL Quote', readonly=True)
    
    dhl_status = fields.Char(
        string='dhl_status',
    )

    campaign = fields.Char(
        string='Campaña',
    )

    guia = fields.Char(
        string='Guía DHL',
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
        compute='_compute_peso_vol'
    )
    
    pesoMasa = fields.Float(
        string='Peso Masa',
        compute='_compute_peso_masa'
    )
    
    pesoEnvio = fields.Float(
        string='Peso a Cotizar',
        compute='_compute_peso_cotizar'
    )

    @api.depends("weight")
    def _compute_peso_masa(self):
        self.pesoMasa = math.ceil(self.weight)

    
    @api.depends("width", "height", "length")
    def _compute_peso_vol(self):
        
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info(self.width)
        _logger.info(self.height)
        _logger.info(self.length)
        
        self.pesoVolumetrico = math.ceil(self.width*self.height*self.length/5000)

        
    @api.depends("pesoVolumetrico", "pesoMasa")
    def _compute_peso_cotizar(self):
        self.pesoEnvio = math.ceil(self.pesoVolumetrico) if self.pesoVolumetrico > self.pesoMasa else math.ceil(self.pesoMasa)

    track_number = fields.Char(
        string='Número de Seguimiento',
    )
    
    track_url = fields.Char(
        string='URL de seguimiento',
    )
    
    dhl_status = fields.Char(
        string='Estado del Envío',
    )
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        domain=[],
        help='Selecciona el cliente asociado con esta orden de compra.'
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
    

    shipping_method = fields.Many2one(
        'dhl.shipping.methods',
        domain=[],
        string='Método de Envío',
        help='Selecciona un método de envío basado en las cotizaciones de DHL.'
    )
    
    
    stored_selection_options = fields.Text(
        string='Stored Selection Options',
        help='Stores the options for the selection field as a JSON string.',
    )

    def set_shipping_method_express(self):
        
        import logging
        _logger = logging.getLogger(__name__)
        
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            metodo = self.shipping_method.search([
                ("name", "ilike", "express domestic"),
                ("purchase_order", "=", po.id),
            ])
            po.shipping_method = metodo.id
            po.dhl_quote = metodo.price
        
        return True

    def set_shipping_method_economy(self):
        
        import logging
        _logger = logging.getLogger(__name__)
        
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            metodo = self.shipping_method.search([
                ("name", "ilike", "economy select domestic"),
                ("purchase_order", "=", po.id),
            ])
            po.shipping_method = metodo.id
            po.dhl_quote = metodo.price
        
        return True

    def execute_request_dhl_quote(self):
        
        import logging
        _logger = logging.getLogger(__name__)
        
        for id in self.env.context.get("active_ids"):
            _logger.info(f"ya estoy funcionando {id}")
            self.env['purchase.order'].browse(id).request_dhl_quote()
        
        return True
    
    def execute_generate_dhl_order(self):
        
        import logging
        _logger = logging.getLogger(__name__)
        
        for id in self.env.context.get("active_ids"):
            _logger.info(f"ya estoy funcionando {id}")
            self.env['purchase.order'].browse(id).generate_dhl_order()
        
        sinSelect = self.env["purchase.order"].search([
            ("guia", "!=", "")
        ])
        
        # for order in sinSelect:
        #     order.button_cancel()

        # _logger.info(f"sin select: {sinSelect}")

        # # sinSelect.unlink()

        return True

    def button_request_dhl_quote(self):
        # Código relacionado con la acción "request_dhl_quote"
        # Sobrescribe este método si necesitas lógica adicional
        return super().button_request_dhl_quote()


    @api.onchange('stored_selection_options')
    def _onchange_field(self):
        if self.stored_selection_options:
            import json
            try:
                options = json.loads(self.stored_selection_options)
                
                import logging
                _logger = logging.getLogger(__name__)
                
                _logger.info(f"options: {options}")
                
                return options
            except json.JSONDecodeError:
                return []
        return []
    

    def request_dhl_quote(self):
        # Ejemplo de datos a enviar a DHL

        import requests
        import logging
        _logger = logging.getLogger(__name__)

        _logger.info(f"self : {self}")        
        _logger.info(f"city : {self.partner_id.city}")        
        _logger.info(f"city dest : {self.customer_id.city}")        
        

        url = "https://express.api.dhl.com/mydhlapi/test/rates"

        _logger.info(f"fecha {self.shipping_date}")

        params = {
            "accountNumber" : "983441463",
            "originCountryCode": self.partner_id.fiscal_country_codes or "MX",
            "originCityName": self.partner_id.city,
            "destinationCountryCode": self.customer_id.fiscal_country_codes or "MX",
            "destinationCityName" : self.customer_id.city,
            "weight": self.pesoEnvio,
            "length" : self.length,
            "width" : self.width,
            "height" : self.height,
            "plannedShippingDate" : self.shipping_date.strftime('%Y-%m-%d'),
            "isCustomsDeclarable" : False,
            "unitOfMeasurement" : "metric",
        }
        
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(
                url,
                auth=('apT3cE5nH6mP9o', 'V#2nZ^1eH$8uU$7n'),
                params=params,
                headers=headers
            )
            if response.status_code == 200:
                quote_data = response.json()
                quote = quote_data["products"][0]["totalPrice"][0]["price"] 
                # _logger.info(f"respuesta: {response.json()}")

                # selection=[('valor1', 'valor1'), ('valor2', 'valor2')]
                products = quote_data.get('products', [])
                if not products:
                    raise UserError(_('No se encontraron métodos de envío disponibles.'))

                # Crear registros para los métodos de envío en el modelo 'dhl.shipping.methods'
                _logger.info(f"id------ {self.id}")
                
                self.env['dhl.shipping.methods'].search([('purchase_order', '=', self.id)]).unlink()

                for product in products:
                    precio = self.env['dhl.shipping.methods'].create({
                        'name': product['productName'] + " - " + f"${product["totalPrice"][0]["price"]:,.2f}",
                        'dhl_code': product['productCode'],
                        'price': product["totalPrice"][0]["price"],
                        'purchase_order': self.id,
                    })
                    _logger.info(f"precio: {precio}")

                # Asignar el primer método de envío como predeterminado (puedes ajustar esto)
                self.shipping_method = self.env['dhl.shipping.methods'].search([('purchase_order', '=', self.id)], limit=1)

                # Notificar al usuario
                self.message_post(body=_('Cotización de DHL completada con los siguientes métodos: %s' % ', '.join([p['productName'] for p in products])))

                metodos = [
                    (product['productCode'], f"{product['productName']} - {product["totalPrice"][0]["price"]}")
                    for product in products
                ]


                _logger.info(f"metodos: {metodos}")
                
                self.stored_selection_options = json.dumps(metodos)
                
                self.dhl_quote = quote
                self.message_post(
                    body=_(f"Se ha obtenido la cotización del envio en DHL: {quote}"),
                )
            else:
                raise Exception(_('Error en la solicitud de cotización de DHL: %s \n %s') % (response.text, response.status_code))
        except Exception as e:
            raise models.UserError(_('No se pudo obtener la cotización de DHL: %s') % str(e))

    def generate_dhl_order(self):

        # obtener tipo de envio:

        metodo = self.shipping_method
        self.dhl_quote = metodo.price
        
        import logging
        _logger = logging.getLogger(__name__)        
        
        formatted_dt = self.shipping_date.strftime("%Y-%m-%dT%H:%M:%S GMT-06:00")
        _logger.info(f"fecha formato {formatted_dt}")

        payload = {
            "plannedShippingDateAndTime": formatted_dt,
            "productCode": metodo.dhl_code,
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
                #         "addressLine1": self.pickup_customer_id.street,
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
                        "countryCode": self.partner_id.fiscal_country_codes or "MX",
                        "addressLine1": self.partner_id.street,
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
                        "issuerCountryCode": self.partner_id.fiscal_country_codes or "MX"
                        }
                    ],
                    "typeCode": "business"
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": self.customer_id.zip,
                        "cityName": self.customer_id.city,
                        "countryCode": self.customer_id.fiscal_country_codes or "MX",
                        "addressLine1": self.customer_id.street,
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
                        "issuerCountryCode": self.customer_id.fiscal_country_codes or "MX"
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
                self.dhl_status = 'Guía Creada'
                self.guia = ''

                pdf_content = data["documents"][0]["content"]
                if not pdf_content:
                    raise UserError(_('No se pudo obtener la etiqueta de envío'))

                # Decodificar el PDF (base64) y adjuntarlo al chatter
                pdf_data = base64.b64decode(pdf_content)
                attachment = self.env['ir.attachment'].create({
                    'name': f'DHL_etiqueta_{self.name}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_data),
                    'res_model': 'purchase.order',
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                # Agregar el adjunto al chatter

                envio = self.env['product.product'].search([
                    ('name', '=', 'Envío DHL')
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
                        'product_id': envio.id,  # Producto "Envío DHL"
                        'name': envio.name + "\n" + metodo.name.split(" - $")[0],  # Nombre del producto
                        'product_qty': 1.0,  # Cantidad
                        'product_uom': envio.uom_id.id,  # Unidad de medida
                        'price_unit': metodo.price,  # Precio del envío
                    })


                self.message_post(
                    body=_("Se ha generado la orden de envío con DHL y se ha adjuntado la etiqueta."),
                    attachment_ids=[attachment.id]
                )
            else:
                raise UserError(_('Error al generar la orden con DHL: %s') % response.text)
        except Exception as e:
            raise UserError(_('No se pudo generar la orden con DHL: %s') % str(e))