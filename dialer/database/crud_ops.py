from peewee import chunked

from dialer.configs import logger
from dialer.configs.settings import Db

from .models import Language, CustomerRecord

log = logger.get_logger()


class CRUD:
    """
    Handle crud operations
    """
    def __init__(self):
        if not Db.is_closed():
            print("Database is already connected.")
        else:
            print("Connecting to the database...")
            Db.connect()
        Db.create_tables([CustomerRecord, Language])

    def create(self, model, **kwargs):
        """
        Create record
        """
        return model.create(**kwargs)

    def read(self, model, filters, columns_to_select=None, join_table = None):
        """
        Read all or specific columns
        """
        if columns_to_select:
            query = model.select(*columns_to_select)
            if join_table:
                query = query.join(join_table)
            return query.where(filters).dicts().iterator()

        query = model.select()
        return query.where(filters).dicts().iterator()

    def update(self, model, filters, **kwargs):
        """
        Update records
        """
        return model.update(**kwargs).where(filters).execute()

    #@staticmethod
    def delete(self, model, filters):
        """
        Delete record
        """
        return model.delete().where(filters).execute()

    def bulk_insert(self, model, data, batch_size):
        """
        Insert many records at once
        """
        try:
            inserted = len(data)
            with Db.atomic():
                for batch in chunked(data, batch_size):
                    model.insert_many(batch).on_conflict_ignore().execute()
            Db.close()
            return inserted

        except RuntimeError as e:
            log.exception("Exception %s:", e)
            raise e

    def read_or_create(self, model, **kwargs):
        """
        Read or create, return record
        """
        instance, _ = model.get_or_create(**kwargs)
        return instance
