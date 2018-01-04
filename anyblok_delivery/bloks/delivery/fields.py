from sqlalchemy.dialects.postgresql import JSONB
from anyblok.column import Column

json_null = object()


class Jsonb(Column):
    """ JSONB column
    """
    sqlalchemy_type = JSONB
    Null = json_null
