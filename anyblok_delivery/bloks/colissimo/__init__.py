from anyblok.blok import Blok
from logging import getLogger
logger = getLogger(__name__)


class DeliveryColissimoBlok(Blok):
    """Delivery blok
    """
    version = "0.1.0"
    author = "Franck BRET"

    required = ['delivery']

    @classmethod
    def import_declaration_module(cls):
        from . import colissimo # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import colissimo
        reload(colissimo)
