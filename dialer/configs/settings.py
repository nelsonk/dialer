import configparser
import os
from datetime import datetime

from peewee import MySQLDatabase


configs = configparser.ConfigParser()
# Get the absolute path to the config file, .. send to parent dir,can use '..', '..' to go 2 dirs up
config_file_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'database.ini')
configs.read(config_file_path)

mydatabase = configs['dialer']['database']
myhost = configs['dialer']['host']
myuser = configs['dialer']['user']
mypassword = configs['dialer']['password']
myport = configs['dialer'].getint('port', 3306)

ami_username = configs['ami']['username']
ami_password = configs['ami']['password']
ami_port = configs['ami']['port']
ami_server = configs['ami']['server']

Db = MySQLDatabase(mydatabase,
                   host = myhost,
                   user = myuser,
                   passwd = mypassword,
                   port = myport)

BATCH_SIZE = 1000

campaign_starts_on = datetime(2024, 7, 14) #change this, start date for compaign yy, mm, dd
DIALPLAN_TARGET_EXTENSION = 999     #used as target in AMI Originate cmd #create function where you pass dialer name and get target, context, logfile
DIALPLAN_CONTEXT = "marketing_dialer"   #used as context in AMI Orignate cmd
START_CALLING_AT = 7
STOP_CALLING_AT = 19

def get_dialer_specific_configs(dialer_name):
    """
    Return dialer specific configs
    """
    asterisk_log_file = os.path.join(os.path.dirname(__file__), "..", "logs", f"asterisk_{dialer_name}.log")
    all_configs = {"asterisk_log_file": asterisk_log_file, "access_log_file": access_log_file, "error_log_file": error_log_file}    
    return all_configs

access_log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', "access.log")
error_log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', "error.log")

