#!/usr/bin/env python3

import sys
import csv
import os
from dialer.database.dbWork import dbWork

class upLoad:
    def __init__(self):
        self.recordsList = []

    def unpackFile(self, file, dialername):
        with open(file, 'r') as infile:
            read = csv.reader(infile)
            next(read) #ignore first row
            for row in read:
                mydict = {"number": row[0], "dialer": dialername, "language": row[1], "type": row[2], "level": 0}
                self.recordsList.append(mydict)
        return self.recordsList

    def dbUpload(self, data):
        result = dbWork().insert(data)
        return result

if __name__ == "__main__": 
    upload = upLoad()
    try:
        file = sys.argv[1]
        dialerName = sys.argv[2]
    except:
        raise Exception("Some arguments not passed")

    mylist = upload.unpackFile(file, dialerName)
    upload.dbUpload(mylist)
