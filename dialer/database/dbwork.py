from datetime import datetime
from peewee import fn, chunked, NodeList, SQL

from .models import record
from configs.settings import Db, batch_size
from configs.logs_configs import Logger


class DbWork:
    def __init__(self):
        self.bath_size = batch_size
        self.log = Logger().get_logger()

    def get(self):
        now = datetime.now().strftime('%Y-%m-%d %H')
        now = f"{now}:00:00"
        records = record.select(record.id, record.number, record.type, record.level, record.language).where((record.run_on == now) | (record.retry == now) | (record.run_on.is_null(True))).dicts().iterator()
        return records
    
    def initial_update(self, id):
        with Db.atomic():
            run_on_interval = NodeList((SQL('INTERVAL'), 7, SQL('DAY')))
            retry_on_interval = NodeList((SQL('INTERVAL'), 1, SQL('DAY')))
            query = record.update(retry = fn.date_add(record.run_on, retry_on_interval), run_on = fn.date_add(record.run_on, run_on_interval)).where(record.id == id)
            print(query.sql())
            my_update = query.execute()
        return print(my_update," record/s updated")
    
    def final_update(self, my_number, my_dialer, date_or_status="successful"):
        my_update = 0
        if date_or_status == "successful":
            with Db.atomic():
                my_update = record.update(retry = None, level = record.level + 1).where((record.number == my_number) & (record.dialer == my_dialer)).execute()
        else:
            if date_or_status is not None:
                with Db.atomic():
                    my_update = record.update(run_on = date_or_status, level = 1).where((record.number == my_number) & (record.dialer == my_dialer)).execute()
        return print(my_update," record/s updated")  
    
    def insert(self, data):
        if not isinstance(data, list):
            self.log.error("Expected a list, rectify or give up")
            raise ValueError("Expected a list, rectify or give up")
        with Db.atomic():
            for batch in chunked(data, self.bath_size):
                inserted = record.insert_many(batch).on_conflict_ignore().execute()
        Db.close()
        return print("SUCCESSFUL <br> ID of last record added is: ", inserted)
