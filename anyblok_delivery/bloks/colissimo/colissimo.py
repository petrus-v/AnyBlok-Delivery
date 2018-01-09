"""Colissimo Carrier Classes
"""
from datetime import datetime
from logging import getLogger

from anyblok import Declarations


logger = getLogger(__name__)
Model = Declarations.Model


@Declarations.register(Model.Carrier.Service, tablename=Model.Carrier.Service)
class Colissimo(Model.Carrier.Service):
    """ The Colissimo Carrier service (Polymorphic model that's override
    Model.Carrier.service)

    Namespace : Model.Carrier.Service.Colissimo
    """
    CARRIER_CODE = "COLISSIMO"
    base_url = "https://ws.colissimo.fr/sls-ws/SlsServiceWSRest/generateLabel"

    def get_carriers(self):
        res = super(Colissimo, self).get_carriers()
        res.update(dict(COLISSIMO='Colissimo'))
        return res

    def get_data(self, shipment=None):
        """Transform database shipment data to colissimo conventions"""
        sh = shipment
        deposit_date = datetime.now().strftime("%Y-%m-%d")
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
                            "firstName": "%s" % sh.sender_address.contact_name,
                            "lastName": "%s" % sh.sender_address.contact_name,
                            "line0": "",
                            "line1": "",
                            "line2": "%s" % sh.sender_address.street1,
                            "line3": "%s" % sh.sender_address.street2,
                            "countryCode": "%s" % sh.sender_address.country,
                            "city": "%s" % sh.sender_address.city,
                            "zipCode": "%s" % sh.sender_address.zip_code,
                            }
                        },
                    "addressee": {
                        "address": {
                            "companyName": "%s" %
                            sh.recipient_address.company_name,
                            "firstName": "%s" %
                            sh.recipient_address.contact_name,
                            "lastName": "%s" %
                            sh.recipient_address.contact_name,
                            "line0": "",
                            "line1": "",
                            "line2": "%s" % sh.recipient_address.street1,
                            "line3": "%s" % sh.recipient_address.street2,
                            "countryCode": "%s" % sh.recipient_address.country,
                            "city": "%s" % sh.recipient_address.city,
                            "zipCode": "%s" % sh.recipient_address.zip_code,
                            }
                        }
                    }
                }
        return data

    def create_label(self, shipment=None):
        data = self.get_data(shipment)
        return data
