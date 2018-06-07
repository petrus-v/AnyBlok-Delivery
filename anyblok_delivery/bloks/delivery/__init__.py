from anyblok.blok import Blok
from logging import getLogger
logger = getLogger(__name__)


class DeliveryBlok(Blok):
    """Delivery blok
    """
    version = "0.1.0"
    author = "Franck BRET"
    required = ['attachment', 'address', 'anyblok-mixins']

    @classmethod
    def import_declaration_module(cls):
        from . import delivery # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import delivery
        reload(delivery)
