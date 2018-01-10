"""Delivery model
"""
from uuid import uuid1
from datetime import datetime
from logging import getLogger

from pycountry import countries

from anyblok import Declarations
from anyblok.column import (
    DateTime,
    UUID,
    String,
    Selection,
    Password
)
from anyblok.relationship import Many2One

from .fields import Jsonb


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
class Address(Mixin.UuidColumn, Mixin.TrackModel):
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
class Carrier(Mixin.UuidColumn, Mixin.TrackModel):
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
class Credential(Mixin.UuidColumn, Mixin.TrackModel):
    """ Store carrier credentials
    Model.Carrier.Credential
    """
    account_number = String(label="Account Number")
    password = String(label="Password", encrypt_key=True)

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

    name = String(label="Name", nullable=False)
    product_code = String(label="Product code", unique=True, nullable=False)
    carrier = Many2One(label="Name",
                       model=Declarations.Model.Carrier,
                       one2many='services',
                       nullable=False)
    credential = Many2One(label="Credential",
                          model=Declarations.Model.Carrier.Credential,
                          one2many='services',
                          nullable=False)
    properties = Jsonb(label="Properties")
    carrier_code = Selection(selections='get_carriers')

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier.Service.{self.carrier_code.label}: {self.name}>')
        return msg.format(self=self)

    @classmethod
    def insert(cls, *args, **kwargs):
        if cls.__registry_name__.startswith('Model.Carrier.Service.'):
            if not kwargs.get('carrier_code'):
                kwargs['carrier_code'] = cls.CARRIER_CODE

        return super(Service, cls).insert(*args, **kwargs)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Service, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Carrier.Service':
            mapper_args.update({'polymorphic_on': cls.carrier_code})

        mapper_args.update({'polymorphic_identity': cls.CARRIER_CODE})
        return mapper_args

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Service, cls).query(*args, **kwargs)
        if cls.__registry_name__.startswith('Model.Carrier.Service.'):
            query = query.filter(cls.carrier_code == cls.CARRIER_CODE)

        return query

    @classmethod
    def get_carriers(cls):
        return dict()

    def create_label(self, *args, **kwargs):
        raise Exception("Creating a label directly from Carrier.Service class "
                        "is Forbidden. Please use a specialized one like "
                        "Colissimo, Dhl, etc...")


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

    def create_label(self):
        """Retrieve a shipping label from shipping service
        """
        if not self.service:
            return
        if not self.status == 'new':
            return
        return self.service.create_label(shipment=self)
