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
            "weight": "1-5",
            "prices": [
              {"flat": 152.0}
            ]
          },
          {
            "weight": 6,
            "prices": [
              {"flat": 160.0}
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
                if isinstance(plan["weight"], int) and plan["weight"] == self.pesoEnvio:
                    precios = ["prices"]
                elif isinstance(plan["weight"], str):
                    weight_range = plan["weight"].split('-')
                    if len(weight_range) == 2 and self.pesoEnvio >= int(weight_range[0]) and self.pesoEnvio <= int(weight_range[1]):
                        precios = ["prices"]
                for key, precio in precios: 
                    _logger.info(f"Creating shipping method for {courier['courier']} {method['method']} {key} ${float(precio):,.2f}")
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
                        'weight': plan["weight"],
                        'origin': self.partner_id.city,
                        'destination': self.customer_id.city,
                        'courier': courier["courier"],
                        'processedBy': 'Emissary',
                        'peakSeason': '',
                    })