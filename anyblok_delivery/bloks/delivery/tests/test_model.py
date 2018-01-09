from anyblok.tests.testcase import BlokTestCase


class TestDeliveryModel(BlokTestCase):
    """ Test delivery model"""

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

    def test_credentials(self):
        cred = self.registry.Carrier.Credential.insert(
                account_number="test", password="xxx")
        self.assertEqual(cred.account_number, 'test')
        self.assertEqual(cred.password, 'xxx')

    def test_addresses(self):
        sender_address = self.create_sender_address()
        recipient_address = self.create_recipient_address()

        self.assertNotEqual(
            sender_address,
            recipient_address
        )
        self.assertEqual(
            self.registry.Address.query().count(),
            2
        )

        self.assertEqual(
            self.registry.Address.query().filter_by(country="FRA").count(),
            2
        )

        self.assertEqual(
            self.registry.Address.query().filter_by(country="USA").count(),
            0
        )
