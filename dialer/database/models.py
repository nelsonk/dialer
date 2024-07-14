import uuid

from peewee import Model, CharField, ForeignKeyField, IntegerField, DateTimeField, SQL, AutoField

from dialer.configs.settings import Db


class BaseModel(Model):
    """
    DB model
    """
    class Meta:
        """
        Specify DB name
        """
        database = Db


class Language(BaseModel):
    """
    Customer Language table model
    """
    customer_language_id = AutoField()
    name = CharField(max_length=50)

    class Meta:
        """
        Specify table name
        """
        table_name = "language"


class CustomerRecord(BaseModel):
    """
    Customer campaign records table model
    """
    id = CharField(primary_key=True, default=lambda: str(uuid.uuid4()), max_length=50)
    phone_number = CharField(max_length=25)
    dialer_name = CharField(max_length=50)
    customer_language_id = ForeignKeyField(Language, backref="records")
    campaign_type = CharField(max_length=50)
    training_level = IntegerField()
    retry_on = DateTimeField(null=True)
    run_on = DateTimeField(null=True)

    class Meta:
        """
        Specify table name
        """
        table_name = "customer"
        constraints = [
            SQL("UNIQUE(phone_number, dialer_name, campaign_type)")
        ]
