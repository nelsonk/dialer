#!/usr/bin/env python3

import sys
import csv

from dialer.database.dbwork import DbWork


class Upload:
    def __init__(self):
        self.records_list = []

    def unpack_file(self, file, dialer_name):
        with open(file, 'r') as in_file:
            read = csv.reader(in_file)
            next(read) #ignore first row
            for row in read:
                my_dict = {"number": row[0], "dialer": dialer_name, "language": row[1], "type": row[2], "level": 0}
                self.records_list.append(my_dict)
        return self.records_list

    def db_upload(self, data):
        result = DbWork().insert(data)
        return result


if __name__ == "__main__": 
    upload = Upload()
    try:
        file = sys.argv[1]
        dialer_name = sys.argv[2]
    except:
        raise Exception("Some arguments not passed")

    my_list = upload.unpack_file(file, dialer_name)
    upload.db_upload(my_list)
