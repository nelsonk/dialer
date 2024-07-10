#!/usr/bin/env python3

import sys
import csv

from database.dbwork import DbWork
from configs.logs_configs import Logger


class Upload:
    def __init__(self):
        self.records_list = []

    def unpack_file(self, file, dialer_name):
        with open(file, 'r') as in_file:
            read = csv.reader(in_file)
            next(read) #ignore first row
            log.info(f"Reading uploaded file {file}, first line ignored")
            for row in read:
                my_dict = {"number": row[0], "dialer": dialer_name, "language": row[1], "type": row[2], "level": 0}
                self.records_list.append(my_dict)
        return self.records_list

    def db_upload(self, data):
        result = DbWork().insert(data)
        return log.info(result)


if __name__ == "__main__": 
    upload = Upload()
    log = Logger().get_logger()
    try:
        file = sys.argv[1]
        dialer_name = sys.argv[2]
    except:
        log.error("Some arguments not passed")
        raise Exception("Some arguments not passed")

    my_list = upload.unpack_file(file, dialer_name)
    upload.db_upload(my_list)
