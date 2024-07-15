#!/usr/bin/env python3

import sys

from dialer.configs import logger
from dialer.database.dbwork import DbWork
from dialer.handlers import files

log = logger.get_logger()


class Upload:
    """
    Logic to read csv and upload to DB
    """
    def __init__(self, uploaded_file, autodialer_name):
        self.records_list = []

        for row in files.Read().get_list_from(uploaded_file):
            self.records_list.append({"phone_number": row[0], "dialer_name": autodialer_name, 
                                      "customer_language_id": row[1], "campaign_type": row[2], "training_level": 0})
                
    def db_upload(self):
        """
        Upload to DB
        """
        log.info(DbWork().insert(self.records_list))


if __name__ == "__main__":
    try:
        file = sys.argv[1]
        dialer_name = sys.argv[2]
    except Exception as e:
        log.exception("Exception %s:", e)
        raise e

    Upload(file, dialer_name).db_upload()
