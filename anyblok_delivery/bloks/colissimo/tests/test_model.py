from unittest.mock import patch
from anyblok.tests.testcase import BlokTestCase


class TestDeliveryModel(BlokTestCase):
    """ Test delivery model"""

    def create_carrier_service_colissimo(self):
        ca = self.registry.Delivery.Carrier.insert(
            name="Colissimo", code="COLISSIMO")
        ca_cred = self.registry.Delivery.Carrier.Credential.insert(
                    account_number="123",
                    password="password")

        service = self.registry.Delivery.Carrier.Service.Colissimo.insert(
                    name="Livraison à domicile", product_code="DOM",
                    carrier=ca, credential=ca_cred)
        return service

    def create_sender_address(self):
        address = self.registry.Address.insert(
                first_name="Shipping",
                last_name="services",
                company_name="Acme",
                street1="1 company street",
                zip_code="75000", state="", city="Paris", country="FRA")
        return address

    def create_recipient_address(self):
        address = self.registry.Address.insert(
                first_name="Jon",
                last_name="Doe",
                street1="1 street",
                street2="crossroad",
                street3="♥",
                zip_code="66000",
                state="A region",
                city="Perpignan",
                country="FRA"
            )
        return address

    def test_carrier_service_colissimo(self):
        colissimo = self.create_carrier_service_colissimo()
        self.assertEqual(
            colissimo.carrier.code,
            "COLISSIMO"
        )

        self.assertEqual(
            len(self.registry.Delivery.Carrier.Service.query().all()),
            1
        )
        self.assertEqual(
            len(self.registry.Delivery.Carrier.Service.Colissimo.query(
            ).all()),
            1
        )

    # def test_carrier_service_colissimo_shipment(self):
    #     colissimo = self.create_carrier_service_colissimo()
    #     sender_address = self.create_sender_address()
    #     recipient_address = self.create_recipient_address()
    #     shipment = self.registry.Delivery.Shipment.insert(
    #             service=colissimo, sender_address=sender_address,
    #             recipient_address=recipient_address,
    #             reason="ORDERXXXXXXXXXX",
    #             pack="PACKXXXXXXXXXX"
    #             )

    #     self.assertEqual(
    #         shipment.service.carrier.code,
    #         "COLISSIMO"
    #     )
    #     self.assertEqual(
    #         shipment.service.product_code,
    #         "DOM"
    #     )
    #     self.assertEqual(
    #         type(shipment.create_label()),
    #         dict
    #     )

    def test_map_data(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )
        data = shipment.service.map_data(shipment=shipment)
        self.assertEqual(
            type(data),
            dict
        )
        self.assertEqual(
            data['letter']['service']['productCode'],
            "DOM"
        )
        self.assertEqual(
            data['letter']['sender']['address']['countryCode'],
            "FR"
        )

    def test_create_label(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Delivery.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address, reason="ORDERXXXXXXXXXX",
                pack="PACKXXXXXXXXXX"
                )

        with patch('anyblok_delivery.bloks.colissimo.colissimo.Colissimo'
                   '.create_label') as mock_post:
            mock_post.return_value = dict(status_code=200)
            response = shipment.create_label()

            self.assertEqual(
                response['status_code'],
                200
            )
