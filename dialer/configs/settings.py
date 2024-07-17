import configparser
import os
from datetime import datetime

from peewee import MySQLDatabase


#We upload heavy CSV files in batches, this sets how many records per batch
BATCH_SIZE = 1000

"""
The context and extension in asterisk dialplan where to send calls
to play training module recordings. These are set in the AMI Originate request
"""
DIALPLAN_TARGET_EXTENSION = 999
DIALPLAN_CONTEXT = "marketing_dialer"

#When the Autodialer should start and stop, outside these hours, it can't run
START_CALLING_AT = 7
STOP_CALLING_AT = 23

#Have listened to recording for at least these seconds to qualify to go to next training module
SUCCESSFUL_AFTER_SECONDS = 10 

"""
This is used to automatically set date the customer should be called basing on 
when campaign is starting. This date should be for a sunday so that if customer chooses
option 1 for monday, we just add one day to this
Format: (yyyy, mm, dd)
"""
campaign_starts_on = datetime(2024, 7, 14) 


def get_file_path(folder_name, file_name):
    """
    Get file path
    """
    file_path = os.path.join(os.getcwd(), f"{folder_name}", f"{file_name}")

    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Ensure the file exists
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass  # Create an empty file

    return file_path


"""
We use configparser to read database and asterisk AMI logins from database.ini
then establish connection to DB.
"""
configs = configparser.ConfigParser()
configs.read(get_file_path("database", "database.ini"))

Db = MySQLDatabase(configs['dialer']['database'],
                   host = configs['dialer']['host'],
                   user = configs['dialer']['user'],
                   passwd = configs['dialer']['password'],
                   port = configs['dialer'].getint('port', 3306))

ami_username = configs['ami']['username']
ami_password = configs['ami']['password']
ami_port = configs['ami']['port']
ami_server = configs['ami']['server']

#Getting path to the log files
access_log_file = get_file_path("logs", "access.log")
error_log_file = get_file_path("logs", "error.log")


def get_dialer_specific_configs(dialer_name):
    """
    Return dialer specific configs mostly the log file asterisk writes to the customer 
    chose of when to be called and length of call which are based on to move customer
    from one training module to another
    """
    return {"asterisk_log_file": get_file_path("logs", f"asterisk_{dialer_name}.log")}
