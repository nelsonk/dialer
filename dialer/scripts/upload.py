#!/usr/bin/env python3

import argparse
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
            run_on = f"{row[3]} {row[4]}"
            self.records_list.append({"phone_number": row[0],
                                      "dialer_name": autodialer_name,
                                      "customer_language_id": row[1],
                                      "campaign_type": row[2],
                                      "run_on": run_on,
                                      "training_level": 1})

    def db_upload(self):
        """
        Upload to DB
        """
        log.info(DbWork().insert(self.records_list))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dialer", help="Specify name of autodialer", type=str)
    parser.add_argument("csv", help="Full path to csv file to upload")

    Upload(parser.parse_args().csv, parser.parse_args().dialer).db_upload()
    sys.exit(0)


if __name__ == "__main__":
    main()
