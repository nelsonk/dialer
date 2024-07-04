import configparser
from peewee import *

config = configparser.ConfigParser()
config.read('database.ini')

mydatabase = config['dialer']['database']
myhost = config['dialer']['host']
myuser = config['dialer']['user']
mypassword = config['dialer']['password']
myport = config['dialer'].getint('port', 3306)

Db = MySQLDatabase(mydatabase,
                   host = myhost,
                   user = myuser,
                   passwd = mypassword,
                   port = myport)

class BaseModel(Model):
    class Meta():
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
