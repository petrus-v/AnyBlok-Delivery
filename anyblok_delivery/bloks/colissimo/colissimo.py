"""Colissimo Carrier Classes
"""
import json
from datetime import datetime
from logging import getLogger

import requests
from requests_toolbelt.multipart import decoder
from pycountry import countries

from anyblok import Declarations


logger = getLogger(__name__)
Model = Declarations.Model


@Declarations.register(Model.Delivery.Carrier)
class Service:

    @classmethod
    def get_carriers(cls):
        res = super(Service, cls).get_carriers()
        res.update(dict(COLISSIMO='Colissimo'))
        return res


@Declarations.register(
    Model.Delivery.Carrier.Service,
    tablename=Model.Delivery.Carrier.Service)
class Colissimo(Model.Delivery.Carrier.Service):
    """ The Colissimo Carrier service (Polymorphic model that's override
    Model.Delivery.Carrier.service)

    Namespace : Model.Delivery.Carrier.Service.Colissimo
    """
    CARRIER_CODE = "COLISSIMO"

    def map_data(self, shipment=None):
        """Given a shipment object, transform its data to Colissimo
        specifications"""
        if not shipment:
            raise Exception("You must pass a shipment object to map_data")

        sh = shipment
        # datetime formatting
        deposit_date = datetime.now().strftime("%Y-%m-%d")
        # 2 letters country code
        sender_country = countries.get(
                alpha_3=sh.sender_address.country).alpha_2
        recipient_country = countries.get(
                alpha_3=sh.recipient_address.country).alpha_2

        data = {"contractNumber": "%s" % self.credential.account_number,
                "password": "%s" % self.credential.password,
                "outputFormat": {
                    "x": "0",
                    "y": "0",
                    "outputPrintingType": "PDF_A4_300dpi"
                    },
                "letter": {
                    "service": {
                        "productCode": "%s" % self.product_code,
                        "depositDate": "%s" % deposit_date,
                        },
                    "parcel": {
                        "weight": "1"
                        },
                    "sender": {
                        "address": {
                            "companyName": "%s" %
                            sh.sender_address.company_name,
                            "firstName": "%s" % sh.sender_address.first_name,
                            "lastName": "%s" % sh.sender_address.last_name,
                            "line0": "",
                            "line1": "",
                            "line2": "%s" % sh.sender_address.street1,
                            "line3": "%s" % sh.sender_address.street2,
                            "countryCode": "%s" % sender_country,
                            "city": "%s" % sh.sender_address.city,
                            "zipCode": "%s" % sh.sender_address.zip_code,
                            }
                        },
                    "addressee": {
                        "address": {
                            "companyName": "%s" %
                            sh.recipient_address.company_name,
                            "firstName": "%s" %
                            sh.recipient_address.first_name,
                            "lastName": "%s" %
                            sh.recipient_address.last_name,
                            "line0": "",
                            "line1": "",
                            "line2": "%s" % sh.recipient_address.street1,
                            "line3": "%s" % sh.recipient_address.street2,
                            "countryCode": "%s" % recipient_country,
                            "city": "%s" % sh.recipient_address.city,
                            "zipCode": "%s" % sh.recipient_address.zip_code,
                            }
                        }
                    }
                }
        return data

    def create_label(self, shipment=None):
        url = \
            "https://ws.colissimo.fr/sls-ws/SlsServiceWSRest/generateLabel"
        data = self.map_data(shipment)
        req = requests.post(url, json=data)
        res = dict()

        # Parse multipart response
        multipart_data = decoder.MultipartDecoder.from_response(req)
        pdf = b''
        infos = dict()

        for part in multipart_data.parts:
            head = dict((item[0].decode(), item[1].decode()) for
                        item in part.headers.lower_items())
            if ("content-type" in head.keys() and
                head.get('content-type', None) ==
                    "application/octet-stream"):
                pdf = part.content
            elif ("content-type" in head.keys() and
                  head.get('content-type', None).startswith(
                      "application/json")):
                infos = json.loads(part.content.decode())

        if req.status_code == 400:
            res['errors'] = infos['messages']
        elif req.status_code == 200:
            res['infos'] = infos
            res['pdf'] = pdf
            shipment.save_document(
                pdf,
                'application/pdf'
            )
            shipment.properties.update({
                'sent': data,
                'received': infos,
            })
            shipment.status = 'Label'

        res['status_code'] = req.status_code
        return res
