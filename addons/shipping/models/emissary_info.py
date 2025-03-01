from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

data = [
  {
    "courier": "99 minutos",
    "methods": [
      {
        "method": "standard",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1": 70.0},
              {"Z2": 75.0},
              {"Z3": 87.0},
              {"Z4": 100.0},
              {"Z5": 246.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1": 80.0},
              {"Z2": 91.0},
              {"Z3": 103.0},
              {"Z4": 119.0},
              {"Z5": 297.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1": 80.0},
              {"Z2": 91.0},
              {"Z3": 103.0},
              {"Z4": 119.0},
              {"Z5": 297.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1": 94.0},
              {"Z2": 107.0},
              {"Z3": 122.0},
              {"Z4": 142.0},
              {"Z5": 355.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1": 167.0},
              {"Z2": 193.0},
              {"Z3": 221.0},
              {"Z4": 253.0},
              {"Z5": 672.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 167.0},
              {"Z2": 193.0},
              {"Z3": 221.0},
              {"Z4": 253.0},
              {"Z5": 672.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"Z1-Z5": 209.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "Fedex",
    "methods": [
      {
        "method": "economico",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z8": 124.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z8": 132.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z8": 139.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1-Z8": 146.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1-Z8": 154.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 160.0},
              {"Z2": 161.0},
              {"Z3": 164.0},
              {"Z4": 167.0},
              {"Z5": 169.0},
              {"Z6": 170.0},
              {"Z7": 172.0}
            ]
          }
        ]
      },
      {
        "method": "express",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 182.0},
              {"Z2": 200.0},
              {"Z3": 217.0},
              {"Z4": 234.0},
              {"Z5": 336.0},
              {"Z6": 339.0},
              {"Z7": 353.0},
              {"Z8": 370.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "DHL",
    "methods": [
      {
        "method": "express",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1": 111.0},
              {"Z2": 113.0},
              {"Z3": 114.0},
              {"Z4": 118.0},
              {"Z5": 133.0},
              {"Z6": 135.0},
              {"Z7": 141.0},
              {"Z8": 145.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1": 111.0},
              {"Z2": 119.0},
              {"Z3": 123.0},
              {"Z4": 125.0},
              {"Z5": 166.0},
              {"Z6": 168.0},
              {"Z7": 175.0},
              {"Z8": 181.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1": 111.0},
              {"Z2": 124.0},
              {"Z3": 131.0},
              {"Z4": 133.0},
              {"Z5": 241.0},
              {"Z6": 243.0},
              {"Z7": 249.0},
              {"Z8": 256.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1": 111.0},
              {"Z2": 137.0},
              {"Z3": 143.0},
              {"Z4": 145.0},
              {"Z5": 314.0},
              {"Z6": 316.0},
              {"Z7": 323.0},
              {"Z8": 329.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1": 119.0},
              {"Z2": 149.0},
              {"Z3": 156.0},
              {"Z4": 158.0},
              {"Z5": 389.0},
              {"Z6": 391.0},
              {"Z7": 397.0},
              {"Z8": 404.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 153.0},
              {"Z2": 163.0},
              {"Z3": 172.0},
              {"Z4": 176.0},
              {"Z5": 461.0},
              {"Z6": 463.0},
              {"Z7": 470.0},
              {"Z8": 476.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"Z1": 165.0},
              {"Z2": 178.0},
              {"Z3": 188.0},
              {"Z4": 194.0},
              {"Z5": 534.0},
              {"Z6": 536.0},
              {"Z7": 542.0},
              {"Z8": 549.0}
            ]
          },
          {
            "weight": 8,
            "prices": [
              {"Z1": 178.0},
              {"Z2": 192.0},
              {"Z3": 205.0},
              {"Z4": 213.0},
              {"Z5": 606.0},
              {"Z6": 608.0},
              {"Z7": 615.0},
              {"Z8": 621.0}
            ]
          },
          {
            "weight": 9,
            "prices": [
              {"Z1": 190.0},
              {"Z2": 207.0},
              {"Z3": 221.0},
              {"Z4": 232.0},
              {"Z5": 678.0},
              {"Z6": 680.0},
              {"Z7": 687.0},
              {"Z8": 693.0}
            ]
          },
          {
            "weight": 10,
            "prices": [
              {"Z1": 203.0},
              {"Z2": 221.0},
              {"Z3": 238.0},
              {"Z4": 251.0},
              {"Z5": 752.0},
              {"Z6": 753.0},
              {"Z7": 759.0},
              {"Z8": 766.0}
            ]
          }
        ]
      },
      {
        "method": "economico",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "UPS",
    "methods": [
      {
        "method": "economico",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z7": 111.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z7": 111.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z7": 111.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1-Z7": 111.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1-Z7": 111.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 184.0},
              {"Z2": 202.0},
              {"Z3": 219.0},
              {"Z4": 236.0},
              {"Z5": 275.0},
              {"Z6": 278.0},
              {"Z7": 290.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"Z1": 200.0},
              {"Z2": 220.0},
              {"Z3": 241.0},
              {"Z4": 258.0},
              {"Z5": 309.0},
              {"Z6": 312.0},
              {"Z7": 326.0}
            ]
          },
          {
            "weight": 8,
            "prices": [
              {"Z1": 216.0},
              {"Z2": 239.0},
              {"Z3": 262.0},
              {"Z4": 279.0},
              {"Z5": 342.0},
              {"Z6": 348.0},
              {"Z7": 364.0}
            ]
          },
          {
            "weight": 9,
            "prices": [
              {"Z1": 232.0},
              {"Z2": 258.0},
              {"Z3": 282.0},
              {"Z4": 301.0},
              {"Z5": 376.0},
              {"Z6": 382.0},
              {"Z7": 400.0}
            ]
          },
          {
            "weight": 10,
            "prices": [
              {"Z1": 248.0},
              {"Z2": 276.0},
              {"Z3": 304.0},
              {"Z4": 322.0},
              {"Z5": 410.0},
              {"Z6": 416.0},
              {"Z7": 437.0}
            ]
          }
        ]
      },
      {
        "method": "express",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1-Z8": 110.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 182.0},
              {"Z2": 200.0},
              {"Z3": 217.0},
              {"Z4": 234.0},
              {"Z5": 336.0},
              {"Z6": 339.0},
              {"Z7": 353.0},
              {"Z8": 370.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"Z1": 198.0},
              {"Z2": 218.0},
              {"Z3": 239.0},
              {"Z4": 255.0},
              {"Z5": 376.0},
              {"Z6": 382.0},
              {"Z7": 399.0},
              {"Z8": 418.0}
            ]
          },
          {
            "weight": 8,
            "prices": [
              {"Z1": 214.0},
              {"Z2": 236.0},
              {"Z3": 260.0},
              {"Z4": 277.0},
              {"Z5": 418.0},
              {"Z6": 424.0},
              {"Z7": 443.0},
              {"Z8": 465.0}
            ]
          },
          {
            "weight": 9,
            "prices": [
              {"Z1": 230.0},
              {"Z2": 255.0},
              {"Z3": 280.0},
              {"Z4": 298.0},
              {"Z5": 458.0},
              {"Z6": 465.0},
              {"Z7": 488.0},
              {"Z8": 513.0}
            ]
          },
          {
            "weight": 10,
            "prices": [
              {"Z1": 246.0},
              {"Z2": 273.0},
              {"Z3": 301.0},
              {"Z4": 319.0},
              {"Z5": 499.0},
              {"Z6": 508.0},
              {"Z7": 532.0},
              {"Z8": 562.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "Paquetexpress",
    "methods": [
      {
        "method": "flat",
        "data": [
          {
            "weight": "1-5",
            "prices": [
              {"flat": 166.0}
            ]
          },
          {
            "weight": "6-10",
            "prices": [
              {"flat": 188.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "Estafeta",
    "methods": [
      {
        "method": "flat",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"flat": 160.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"flat": 168.0}
            ]
          },
          {
            "weight": 8,
            "prices": [
              {"flat": 176.0}
            ]
          },
          {
            "weight": 9,
            "prices": [
              {"flat": 184.0}
            ]
          },
          {
            "weight": 10,
            "prices": [
              {"flat": 191.0}
            ]
          }
        ]
      }
    ]
  },
  {
    "courier": "AM PM",
    "methods": [
      {
        "method": "standard",
        "data": [
          {
            "weight": 1,
            "prices": [
              {"Z1-Z8": 80.0}
            ]
          },
          {
            "weight": 2,
            "prices": [
              {"Z1-Z8": 80.0}
            ]
          },
          {
            "weight": 3,
            "prices": [
              {"Z1-Z8": 80.0}
            ]
          },
          {
            "weight": 4,
            "prices": [
              {"Z1": 98.0},
              {"Z2": 103.0},
              {"Z3": 109.0},
              {"Z4": 114.0},
              {"Z5": 122.0},
              {"Z6": 132.0},
              {"Z7": 142.0},
              {"Z8": 153.0}
            ]
          },
          {
            "weight": 5,
            "prices": [
              {"Z1": 98.0},
              {"Z2": 103.0},
              {"Z3": 109.0},
              {"Z4": 114.0},
              {"Z5": 122.0},
              {"Z6": 132.0},
              {"Z7": 142.0},
              {"Z8": 153.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"Z1": 124.0},
              {"Z2": 131.0},
              {"Z3": 138.0},
              {"Z4": 145.0},
              {"Z5": 156.0},
              {"Z6": 167.0},
              {"Z7": 179.0},
              {"Z8": 193.0}
            ]
          },
          {
            "weight": 7,
            "prices": [
              {"Z1": 124.0},
              {"Z2": 131.0},
              {"Z3": 138.0},
              {"Z4": 145.0},
              {"Z5": 156.0},
              {"Z6": 167.0},
              {"Z7": 179.0},
              {"Z8": 193.0}
            ]
          },
          {
            "weight": 8,
            "prices": [
              {"Z1": 124.0},
              {"Z2": 131.0},
              {"Z3": 138.0},
              {"Z4": 145.0},
              {"Z5": 156.0},
              {"Z6": 167.0},
              {"Z7": 179.0},
              {"Z8": 193.0}
            ]
          },
          {
            "weight": 9,
            "prices": [
              {"Z1": 124.0},
              {"Z2": 131.0},
              {"Z3": 138.0},
              {"Z4": 145.0},
              {"Z5": 156.0},
              {"Z6": 167.0},
              {"Z7": 179.0},
              {"Z8": 193.0}
            ]
          },
          {
            "weight": 10,
            "prices": [
              {"Z1": 124.0},
              {"Z2": 131.0},
              {"Z3": 138.0},
              {"Z4": 145.0},
              {"Z5": 156.0},
              {"Z6": 167.0},
              {"Z7": 179.0},
              {"Z8": 193.0}
            ]
          }
        ]
      }
    ]
  }
]

def get_price_plans(self):
    for courier in data:
        for method in courier["methods"]:
            for plan in method["data"]:
                precios = []
                _logger.info(f"pesoEnvio: {self.pesoEnvio}")
                _logger.info(f"plan: {plan}")
                _logger.info(f"weight: {plan["weight"]}")
                if isinstance(plan["weight"], int) and plan["weight"] == self.pesoEnvio:
                    precios = plan["prices"]
                elif isinstance(plan["weight"], str):
                    weight_range = plan["weight"].split('-')
                    if len(weight_range) == 2 and self.pesoEnvio >= int(weight_range[0]) and self.pesoEnvio <= int(weight_range[1]):
                        precios = plan["prices"]

                _logger.info(f"precios: {precios}")
                for price in precios:
                    for key, precio in price.items():
                        _logger.info(f"Creating shipping method for {courier['courier']} {method['method']} {key} ${float(precio):,.2f}, con la orden de compra {self.id}")
                        self.env['shipping.methods'].create({
                            'name': courier["courier"] + " " + method["method"] + " " + key + f" ${float(precio):,.2f}",
                            'shipping_code': key,
                            'price': precio,
                            'purchase_order': self.id,
                            'basePrice': '',
                            'discount': '',
                            'tax': '',
                            'fuelSurcharge': '',
                            'remoteArea': '',
                            'requestDate': datetime.now(),
                            'weight': self.pesoEnvio,
                            'origin': self.partner_id.city,
                            'destination': self.customer_id.city,
                            'courier': courier["courier"],
                            'processedBy': 'Emissary',
                            'peakSeason': '',
                        })