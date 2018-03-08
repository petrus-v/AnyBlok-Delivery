"""Delivery model
"""
from uuid import uuid1
from datetime import datetime
from logging import getLogger

from anyblok import Declarations
from anyblok.column import (
    DateTime,
    UUID,
    String,
    Selection
)
from anyblok.relationship import Many2One
from anyblok.field import Function
from anyblok_postgres.column import Jsonb
import hashlib


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
class Delivery:
    """Namespace for deliveries"""


@Declarations.register(Model.Delivery)
class Carrier(Mixin.UuidColumn, Mixin.TrackModel):
    """ 'Model.Delivery.Carrier' namespace
    """
    name = String(label="Name", nullable=False)
    code = String(label="Code", unique=True, nullable=False)

    def __str__(self):
        return ('{self.name}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier: {self.name} - {self.code}>')

        return msg.format(self=self)


@Declarations.register(Model.Delivery.Carrier)
class Credential(Mixin.UuidColumn, Mixin.TrackModel):
    """ Store carrier credentials
    Model.Delivery.Carrier.Credential
    """
    account_number = String(label="Account Number")
    password = String(label="Password", encrypt_key=True)

    def __str__(self):
        return ('{self.account_number}').format(self=self)

    def __repr__(self):
        msg = ('<Carrier.Credential: {self.account_number}>')

        return msg.format(self=self)


@Declarations.register(Model.Delivery.Carrier)
class Service(Mixin.UuidColumn, Mixin.TrackModel):
    """ Carrier service
    Model.Delivery.Carrier.Service
    """
    CARRIER_CODE = None

    name = String(label="Name", nullable=False)
    product_code = String(label="Product code", unique=True, nullable=False)
    carrier = Many2One(label="Name",
                       model=Declarations.Model.Delivery.Carrier,
                       one2many='services',
                       nullable=False)
    credential = Many2One(label="Credential",
                          model=Declarations.Model.Delivery.Carrier.Credential,
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
    def define_mapper_args(cls):
        mapper_args = super(Service, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Delivery.Carrier.Service':
            mapper_args.update({'polymorphic_on': cls.carrier_code})

        mapper_args.update({'polymorphic_identity': cls.CARRIER_CODE})
        return mapper_args

    @classmethod
    def query(cls, *args, **kwargs):
        query = super(Service, cls).query(*args, **kwargs)
        if cls.__registry_name__.startswith('Model.Delivery.Carrier.Service.'):
            query = query.filter(cls.carrier_code == cls.CARRIER_CODE)

        return query

    @classmethod
    def get_carriers(cls):
        return dict()

    def create_label(self, *args, **kwargs):
        raise Exception("Creating a label directly from Carrier.Service class "
                        "is Forbidden. Please use a specialized one like "
                        "Colissimo, Dhl, etc...")


@Declarations.register(Model.Delivery)
class Shipment(Mixin.UuidColumn, TrackModel):
    """ Shipment
    """
    statuses = dict(new="New", label="Label", transit="Transit",
                    delivered="Delivered", exception="Exception")
    service = Many2One(label="Shipping service",
                       model=Declarations.Model.Delivery.Carrier.Service,
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
    reason = String(label="Reason reference")
    pack = String(label="Pack reference")
    status = Selection(label="Shipping status", selections=statuses,
                       default='new',
                       nullable=False)
    properties = Jsonb(label="Properties")
    document_uuid = UUID(label="Carrier slip document reference")
    document = Function(fget='get_latest_document')
    tracking_number = String(label="Carrier tracking number")

    def get_latest_document(self):
        Document = self.registry.Attachment.Document.Latest
        query = Document.query().filter_by(uuid=self.document_uuid)
        return query.one_or_none()

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

    def save_document(self, binary_file, content_type):
        document = self.document
        if document is None:
            document = self.registry.Attachment.Document.insert(
                data={'shipment': str(self.uuid)}
            )
            self.document_uuid = document.uuid

        document.file = binary_file
        document.filesize = len(binary_file)
        document.contenttype = content_type
        hash = hashlib.sha256()
        hash.update(binary_file)
        document.hash = hash.digest()

        self.registry.flush()  # flush to update version in document
