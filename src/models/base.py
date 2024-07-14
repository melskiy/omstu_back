from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData


metadata_obj = MetaData(schema='omstu_practice')

Base = declarative_base(metadata=metadata_obj)
