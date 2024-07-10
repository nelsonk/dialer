from peewee import *

from configs.settings import Db


class BaseModel(Model):
    class Meta:
        database = Db

class record(BaseModel):
    id = IntegerField(primary_key=True)
    number = IntegerField()
    dialer = CharField(max_length=255)
    language = CharField(max_length=255)
    type = CharField(max_length=255)
    level = IntegerField()
    retry = DateTimeField()
    run_on = DateTimeField()

    class Meta:
        table_name = "list"
