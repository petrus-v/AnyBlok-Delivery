"""Delivery model
"""
from uuid import uuid1
from datetime import datetime

from pycountry import countries

from anyblok import Declarations
from anyblok.column import DateTime, UUID, String, Selection, Password
from anyblok.relationship import Many2One

from .fields import Jsonb
from logging import getLogger


logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin


@Declarations.register(Mixin)
class UuidColumn:
    """ `UUID` id primary key mixin
    """
    uuid = UUID(primary_key=True, default=uuid1, binary=False)


@Declarations.register(Mixin)
class TrackModel:
    """ A mixin to store record creation and edition date
    """
    create_date = DateTime(default=datetime.now, nullable=False)
    edit_date = DateTime(default=datetime.now, nullable=False,
                         auto_update=True)


@Declarations.register(Declarations.Model)
class Address(Mixin.UuidColumn, TrackModel):
    """ Postal address for delivery
    """
    countries = dict((country.alpha_3, country.name) for country in countries)

    contact_name = String(label="Contact name", nullable=False)
    company_name = String(label="Company name")
    street1 = String(label="Street line 1", nullable=False)
    street2 = String(label="Street line 2")
    street3 = String(label="Street line 3")
    zip_code = String(label="Postal Code")
    state = String(label="State")
    city = String(label="City", nullable=False)
    country = Selection(label="Country", selections=countries, nullable=False)
    phone1 = String(label="Phone 1")
    phone2 = String(label="Phone 2")
    email = String(label="Email")

    def __str__(self):
        return ('{self.uuid}').format(self=self)

    def __repr__(self):
        msg = ('<Address: {self.uuid}, {self.contact_name}, '
               '{self.company_name}, {self.zip_code}, {self.country}>')

        return msg.format(self=self)


@Declarations.register(Model)
class Carrier(Mixin.UuidColumn, TrackModel):
    """ 'Model.Carrier' namespace
    """
    name = String(label="Name", nullable=False)
    code = String(label="Code", unique=True, nullable=False)

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier: {self.name} - {self.code}>')

        return msg.format(self=self)


@Declarations.register(Model.Carrier)
class Credential(Mixin.UuidColumn, TrackModel):
    """ Store carrier credentials
    Model.Carrier.Credential
    """
    account_number = String(label="Account Number")
    password = Password(crypt_context={'schemes': ['pbkdf2_sha512']},
                        nullable=False)

    def __str__(self):
        return ('{self.account_number}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier.Credential: {self.account_number}>')

        return msg.format(self=self)


@Declarations.register(Model.Carrier)
class Service(Mixin.UuidColumn, TrackModel):
    """ Carrier service
    Model.Carrier.Service
    """
    CARRIER_CODE = None

    name = String(label="Name", unique=True, nullable=False)
    carrier = Many2One(label="Name",
                       model=Declarations.Model.Carrier,
                       one2many='services',
                       nullable=False)
    credential = Many2One(label="Credential",
                          model=Declarations.Model.Carrier.Credential,
                          one2many='services',
                          nullable=False)
    properties = Jsonb(label="Properties")

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier.Service: {self.name}>')

        return msg.format(self=self)

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Service, cls).query(*args, **kwargs)
        if cls.__registry_name__.startswith('Model.Carrier.Service.'):
            carrier = cls.registry.Carrier.query().filter_by(
                code=cls.CARRIER_CODE).first()
            query = query.filter(cls.carrier == carrier)

        return query


@Declarations.register(Model.Carrier.Service)
class Colissimo(Model.Carrier.Service):
    """ Carrier service
    Model.Carrier.Service.Colissimo
    """
    CARRIER_CODE = "COLISSIMO"


@Declarations.register(Model.Carrier.Service)
class Dhl(Model.Carrier.Service):
    """ Carrier service
    Model.Carrier.Service.Dhl
    """
    CARRIER_CODE = "DHL"


@Declarations.register(Model)
class Shipment(Mixin.UuidColumn, TrackModel):
    """ Shipment
    """
    statuses = dict(new="New", label="Label", transit="Transit",
                    delivered="Delivered", exception="Exception")
    service = Many2One(label="Shipping service",
                       model=Declarations.Model.Carrier.Service,
                       one2many='shipments',
                       nullable=False)
    sender_address = Many2One(label="Sender address",
                              model=Declarations.Model.Address,
                              column_names=["sender_address_uuid"],
                              nullable=False)
    recipient_address = Many2One(label="Recipient address",
                                 model=Declarations.Model.Address,
                                 column_names=["recipient_address_uuid"],
                                 nullable=False)
    status = Selection(label="Shipping status", selections=statuses,
                       default='new',
                       nullable=False)
    properties = Jsonb(label="Properties")

    def __str__(self):
        return ('{self.uuid}').format(self=self)

    def __repr__(self):
        msg = ('<Shipment: {self.uuid}>')

        return msg.format(self=self)
