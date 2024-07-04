from dialer.database.models import record, Db
from datetime import datetime
from peewee import fn, chunked, NodeList, SQL


class dbWork:
    def __init__(self):
        self.bath_size = 1000

    def get(self):
        now = datetime.now().strftime('%Y-%m-%d %H')
        now = f"{now}:00:00"
        records = record.select(record.id, record.number, record.type, record.level, record.language).where((record.run_on == now) | (record.retry == now) | (record.run_on.is_null(True))).dicts().iterator()
        return records
    
    def initialUpdate(self, id):
        with Db.atomic():
            interval = NodeList((SQL('INTERVAL'), 7, SQL('DAY')))
            retryInterval = NodeList((SQL('INTERVAL'), 1, SQL('DAY')))
            myupdate = record.update(retry = fn.date_add(record.run_on, retryInterval), run_on = fn.date_add(record.run_on, interval)).where(record.id == id).execute()
        return print(myupdate," record/s updated")
    
    def finalUpdate(self, mynumber, mydialer, dateOrStatus="successful"):
        myupdate = 0
        if dateOrStatus == "successful":
            with Db.atomic():
                myupdate = record.update(retry = None, level = record.level + 1).where((record.number == mynumber) & (record.dialer == mydialer)).execute()
        else:
            if dateOrStatus is not None:
                with Db.atomic():
                    myupdate = record.update(run_on = dateOrStatus, level = 1).where((record.number == mynumber) & (record.dialer == mydialer)).execute()
        return print(myupdate," record/s updated")  
    
    def insert(self, data):
        if not isinstance(data, list):
            raise ValueError("Expected a list, rectify or give up")
        with Db.atomic():
            for batch in chunked(data, self.bath_size):
                inserted = record.insert_many(batch).on_conflict_ignore().execute()
        Db.close()
        return print("SUCCESSFUL <br> ID of last record added is: ", inserted)