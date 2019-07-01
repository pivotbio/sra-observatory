import os

from peewee import *
from playhouse.postgres_ext import BinaryJSONField


def load_database_config():
    return {
        "name": os.getenv("SOBS_DB_NAME"),
        "user": os.getenv("SOBS_DB_USER"),
        "password": os.getenv("SOBS_DB_PASSWORD"),
        "port": os.getenv("SOBS_DB_PORT"),
        "host": os.getenv("SOBS_DB_HOST"),
    }


def get_database():
    config = load_database_config()
    db = PostgresqlDatabase(
        config["name"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
    )
    return db


class Base(Model):
    class Meta:
        database = get_database()


class Sample(Base):
    id = CharField(primary_key=True, index=True)
    taxid = IntegerField(null=True, index=True)
    attributes = BinaryJSONField()

    scientific_name = CharField(null=True)


class Experiment(Base):

    id = CharField(primary_key=True, index=True)
    sample_accession = CharField(null=True, index=True)
    description = TextField(null=True)

    library_name = CharField(null=True)
    library_strategy = CharField(null=True)
    library_source = CharField(null=True)
    library_selection = CharField(null=True)
    library_layout = CharField(null=True)
    platform_type = CharField(null=True)
    platform_instrument_model = CharField(null=True)


class Run(Base):
    id = CharField(primary_key=True, index=True)

    experiment_accession = CharField(null=True, index=True)
    title = CharField(null=True)
