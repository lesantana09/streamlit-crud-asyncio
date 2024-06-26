from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.utils.singleton import SingletonHash


class BaseOrm(metaclass=SingletonHash):
    def __init__(self, database_uri: str):

        self.__engine = create_engine(
            url=database_uri,
            pool_size=20,
            pool_recycle=10,
            max_overflow=10,
            pool_timeout=10
        )
        self.__session = scoped_session(sessionmaker(
            bind=self.__engine, autocommit=False, autoflush=True))


    @property
    def engine(self):
        return self.__engine

    @property
    def session(self):
        return self.__session