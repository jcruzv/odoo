from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
import json
import base64

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    dhl_quote = fields.Float(string='DHL Quote', readonly=True)
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        domain=[],
        help='Selecciona el cliente asociado con esta orden de compra.'
    )

    shipping_method = fields.Many2one(
        'x_shipping.method',
        domain=[],
        string='Método de Envío',
        help='Selecciona un método de envío basado en las cotizaciones de DHL.'
    )
    
    
    stored_selection_options = fields.Text(
        string='Stored Selection Options',
        help='Stores the options for the selection field as a JSON string.',
    )

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

        params = {
            "accountNumber" : "983441463",
            "originCountryCode": "MX",
            "originCityName": self.partner_id.city,
            "destinationCountryCode": "MX",
            "destinationCityName" : self.customer_id.city,
            "weight": "5",  # Peso en kg
            "length" : "5",
            "width" : "5",
            "height" : "5",
            "plannedShippingDate" : "2025-01-22",
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

                # Crear registros para los métodos de envío en el modelo 'shipping.method'
                _logger.info(f"id------ {self.id}")
                
                self.env['x_shipping.method'].search([('x_purchase_order', '=', self.id)]).unlink()

                for product in products:
                    precio = self.env['x_shipping.method'].create({
                        'x_name': product['productName'],
                        'x_dhl_code': product['productCode'],
                        'x_price': product["totalPrice"][0]["price"],
                        'x_purchase_order': self.id,
                    })
                    _logger.info(f"precio: {precio}")

                # Asignar el primer método de envío como predeterminado (puedes ajustar esto)
                self.shipping_method = self.env['x_shipping.method'].search([], limit=1)

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
        

        payload = {
            "plannedShippingDateAndTime": "2025-01-22T19:19:40 GMT+00:00",
            "pickup": {
                "isRequested": False
            },
            "productCode": "N",
            "getRateEstimates": False,
            "accounts": [
                {
                    "number": "983441463",
                    "typeCode": "shipper"
                }
            ],
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
                        "postalCode": "57000",
                        "cityName": "Nezahualcoyotl",
                        "countryCode": "MX",
                        "addressLine1": "El Abandonado 363",
                    },
                    "contactInformation": {
                        "email": "shipper_create_shipmentapi@dhltestmail.com",
                        "phone": "5523088355",
                        "companyName": "DPR Wholesalers",
                        "fullName": "Johnny Steward"
                    },
                    "registrationNumbers": [
                        {
                        "typeCode": "VAT",
                        "number": "244444911",
                        "issuerCountryCode": "MX"
                        }
                    ],
                    "typeCode": "business"
                },
                "receiverDetails": {
                    "postalAddress": {
                        "postalCode": "57000",
                        "cityName": "Nezahualcoyotl",
                        "countryCode": "MX",
                        "addressLine1": "Cascabel 201",    
                    },
                    "contactInformation": {
                        "email": "recipient_create_shipmentapi@dhltestmail.com",
                        "phone": "1123123",
                        "companyName": "DoCo Event Airline Catering",
                        "fullName": "Jorge Cruz"
                    },
                    "registrationNumbers": [
                        {
                        "typeCode": "VAT",
                        "number": "12345678",
                        "issuerCountryCode": "MX"
                        }
                    ],
                    "typeCode": "business"
                }
            },
            "content": {
                "packages": [
                {
                    "typeCode": "2BP",
                    "weight": 5,
                    "dimensions": {
                    "length": 1,
                    "width": 1,
                    "height": 1
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
                
                pdf_content = data["documents"][0]["content"]
                if not pdf_content:
                    raise UserError(_('No se pudo obtener la etiqueta de envío'))

                # Decodificar el PDF (base64) y adjuntarlo al chatter
                pdf_data = base64.b64decode(pdf_content)
                attachment = self.env['ir.attachment'].create({
                    'name': f'DHL_Shipment_Label_{self.name}.pdf',
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_data),
                    'res_model': 'purchase.order',
                    'res_id': self.id,
                    'mimetype': 'application/pdf',
                })
                # Agregar el adjunto al chatter
                self.message_post(
                    body=_("Se ha generado la orden de envío con DHL y se ha adjuntado la etiqueta."),
                    attachment_ids=[attachment.id]
                )
            else:
                raise UserError(_('Error al generar la orden con DHL: %s') % response.text)
        except Exception as e:
            raise UserError(_('No se pudo generar la orden con DHL: %s') % str(e))