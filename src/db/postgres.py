import os
from decouple import config

class PostgresOrm:
    def get_orm(self, base_orm):
        return base_orm

    def get_database_uri(self) -> str:
        db_user = config("POSTGRES_USER", cast=str)
        db_password = config("POSTGRES_PASSWORD", cast=str)
        db_name = config("POSTGRES_DB", cast=str)
        db_host = "localhost"
        db_port = 5432
        database_uri = f"postgresql://{db_user}:{db_password}"
        database_uri += f"@{db_host}:{db_port}"
        database_uri += f"/{db_name}"
        return database_uri