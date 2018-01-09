from anyblok.tests.testcase import BlokTestCase


class TestDeliveryModel(BlokTestCase):
    """ Test delivery model"""

    def create_carrier_service_colissimo(self):
        ca = self.registry.Carrier.insert(name="Colissimo", code="COLISSIMO")
        ca_cred = self.registry.Carrier.Credential.insert(
                    account_number="123456",
                    password="password")
        service = self.registry.Carrier.Service.Colissimo.insert(
                    name="Livraison à domicile", product_code="DOM",
                    carrier=ca, credential=ca_cred)
        return service

    def create_sender_address(self):
        address = self.registry.Address.insert(
                contact_name="Shipping services",
                company_name="Acme",
                street1="1 company street",
                zip_code="00000", state="", city="There", country="FRA")
        return address

    def create_recipient_address(self):
        address = self.registry.Address.insert(
                contact_name="Jon Doe",
                street1="1 street",
                street2="crossroad",
                street3="♥",
                zip_code="99999",
                state="A region",
                city="Nowhere",
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
            len(self.registry.Carrier.Service.query().all()),
            1
        )
        self.assertEqual(
            len(self.registry.Carrier.Service.Colissimo.query().all()),
            1
        )
        self.assertEqual(
            len(self.registry.Carrier.Service.Dhl.query().all()),
            0
        )

    def test_carrier_service_colissimo_shipment(self):
        colissimo = self.create_carrier_service_colissimo()
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()
        shipment = self.registry.Shipment.insert(
                service=colissimo, sender_address=sender_address,
                recipient_address=recipient_address)

        self.assertEqual(
            shipment.service.carrier.code,
            "COLISSIMO"
        )
        self.assertEqual(
            shipment.service.product_code,
            "DOM"
        )
        self.assertEqual(
            type(shipment.create_label()),
            dict
        )
