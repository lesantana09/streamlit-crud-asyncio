import importlib
from src.db.base_orm import BaseOrm


class DatabaseSessionMixin:

    def __enter__(self):
        module = getattr(
            importlib.import_module("src.db.postgres"),
            "PostgresOrm",
        )
        orm_module = module()
        database_uri = orm_module.get_database_uri()
        orm = orm_module.get_orm(base_orm=BaseOrm(database_uri=database_uri))
        self.session = orm.session
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is not None:
                self.session.rollback()

        except Exception as error:
            raise Exception(error)
        finally:
            self.session.close()


def use_database_session() -> DatabaseSessionMixin:
    return DatabaseSessionMixin()