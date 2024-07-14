from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.settings import settings
from sqlalchemy.engine import URL


connection_string = URL.create(
    drivername='postgresql+asyncpg',
    username=settings.login,
    password=settings.password,
    host=settings.base_host,
    port=settings.base_port,
    database=settings.base_name,
)


engine = create_async_engine(
    connection_string
)

Session = async_sessionmaker(
    engine,
    autocommit=False,
    autoflush=False,
)


#def get_session():
    #session = Session()
    #try:
    #    yield session
    #finally:
    #   session.close()
