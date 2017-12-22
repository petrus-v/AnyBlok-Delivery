from anyblok_pyramid_rest_api.validator import (
    model_schema_validator, full_validator)
from anyblok_pyramid_rest_api.crud_resource import CrudResource, get
from anyblok_pyramid import current_blok


MODEL = 'Model.Delivery'


@resource(
    collection_path='deliveries',
    path='deliveries/{uuid}',
    validators=(model_schema_validator,),
    installed_blok=current_blok()
)
class DeliveryResource(CrudResource):
    model = MODEL
