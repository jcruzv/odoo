from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import requests
import json
import base64
import math

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_dhl_events_action(self):
        """Retorna la acción para mostrar los eventos relacionados con la orden de compra."""
        self.ensure_one()  # Asegúrate de que solo se está llamando en un registro
        action = self.env.ref('dhl_events.action_dhl_events_view').read()[0]
        action['domain'] = [('purchase_order', '=', self.id)]
        return action


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

    
    method_basePrice = fields.Float(
        related='shipping_method.basePrice', 
        string="Precio Base", 
        store=True
    )
    method_discount = fields.Float(
        related='shipping_method.discount', 
        string="Descuento", 
        store=True
    )
    method_tax = fields.Float(
        related='shipping_method.tax', 
        string="Impuesto", 
        store=True
    )
    
    dhl_quote = fields.Float(string='Total Envío', readonly=True)
    
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
    
    campaign = fields.Many2one(
        'purchase.campaigns',
        string='Campaña',
        domain=[],
        help='Selecciona la Campaña relacionada a esta orden.'
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
        
        for id in self.env.context.get("active_ids"):
            po = self.env['purchase.order'].browse(id)
            metodo = self.shipping_method.search([
                ("name", "ilike", "economy select domestic"),
                ("purchase_order", "=", po.id),
            ])
            po.shipping_method = metodo.id
            po.dhl_quote = metodo.price
        
        return True


    def execute_request_dhl_track(self):
        
        for id in self.env.context.get("active_ids"):
            self.env['purchase.order'].browse(id).track()
        
        return True

    def execute_request_dhl_quote(self):
        
        for id in self.env.context.get("active_ids"):
            self.env['purchase.order'].browse(id).request_dhl_quote()
        
        return True
    
    def execute_generate_dhl_order(self):
        
        for id in self.env.context.get("active_ids"):
            self.env['purchase.order'].browse(id).generate_dhl_order()
        
        # sinSelect = self.env["purchase.order"].search([
        #     ("guia", "!=", "")
        # ])
        
        # for order in sinSelect:
        #     order.button_cancel()

        # _logger.info(f"sin select: {sinSelect}")

        # # sinSelect.unlink()

        return True

    def button_request_dhl_quote(self):
        return super().button_request_dhl_quote()


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
        if not self.partner_id: 
            raise UserError("No has asignado Proveedor")
        if not self.customer_id: 
            raise UserError("No has asignado Cliente")
        if not self.partner_id.country_code: 
            raise UserError("El Proveedor no tiene el campo 'País' asignado correctamente")
        if not self.partner_id.city: 
            raise UserError("El Proveedor no tiene el campo 'Ciudad' asignado correctamente")
        if not self.customer_id.country_code: 
            raise UserError("El Cliente no tiene el campo 'País' asignado correctamente")
        if not self.customer_id.city: 
            raise UserError("El Cliente no tiene el campo 'Ciudad' asignado correctamente")
        if not self.weight or self.weight <= 0: 
            raise UserError("El campo 'Peso' es incorrecto")
        if not self.length or self.length <= 0: 
            raise UserError("El campo 'Largo' es incorrecto")
        if not self.width or self.width <= 0: 
            raise UserError("El campo 'Ancho' es incorrecto")
        if not self.height or self.height <= 0: 
            raise UserError("El campo 'Alto' es incorrecto")

    def request_dhl_quote(self):
        # Ejemplo de datos a enviar a DHL

        import requests
        import logging
        _logger = logging.getLogger(__name__)  
        

        url = "https://express.api.dhl.com/mydhlapi/test/rates"

        self.Validar()

        date = datetime.now() + timedelta(minutes=5)

        params = {
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
                _logger.info(f"productos------ {products}")
                
                self.env['dhl.shipping.methods'].search([('purchase_order', '=', self.id)]).unlink()

                for product in products:
                    if product['productName'] and product['productName'] in ['ECONOMY SELECT DOMESTIC', 'EXPRESS DOMESTIC', 'DOMESTICO ENVIO RETORNO']:
                        precio = self.env['dhl.shipping.methods'].create({
                            'name': product['productName'] + " - " + f"${product["totalPrice"][0]["price"]:,.2f}",
                            'dhl_code': product['productCode'],
                            'price': product["totalPrice"][0]["price"],
                            'purchase_order': self.id,
                            'basePrice': next(item["price"] for item in product["totalPriceBreakdown"][0]["priceBreakdown"] if item["typeCode"] == "SPRQT"),
                            'discount': next(item["price"] for item in product["totalPriceBreakdown"][0]["priceBreakdown"] if item["typeCode"] == "STDIS"),
                            'tax': next(item["price"] for item in product["totalPriceBreakdown"][0]["priceBreakdown"] if item["typeCode"] == "STTXA"),
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
        
        date = datetime.now() + timedelta(minutes=5)
        formatted_dt = date.strftime("%Y-%m-%dT%H:%M:%S GMT-06:00")
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
                        "countryCode": self.partner_id.country_code or "MX",
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
        


    def track(self):
        # Ejemplo de datos a enviar a DHL

        import requests
        import logging
        _logger = logging.getLogger(__name__)  
        

        url = "https://express.api.dhl.com/mydhlapi/test/shipments/" + self.track_number + "/tracking"
        
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
                url,
                auth=('apT3cE5nH6mP9o', 'V#2nZ^1eH$8uU$7n'),
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()

                _logger.info(data)
                # self.dhl_status = data['shipments'][0]['estimatedDeliveryDate']
                self.env['dhl.shipping.events'].search([('purchase_order', '=', self.id)]).unlink()
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
                    self.env['dhl.shipping.events'].create({
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

                    self.dhl_status = classification_found
                else:
                    self.dhl_status = 'Registrado'
                    

            else:
                raise Exception(_('Error en la solicitud de tracking de DHL: %s \n %s') % (response.text, response.status_code))
        except Exception as e:
            raise models.UserError(_('No se pudo obtener el estado de DHL: %s') % str(e))
