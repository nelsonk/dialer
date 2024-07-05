from configparser import ConfigParser
from peewee import MySQLDatabase
from datetime import datetime


configs = ConfigParser('database/database.ini')
configs.read()

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

batch_size = 1000

campaign_starts_on = datetime(2024, 5, 26) #change this, start date for compaign
asterisk_log_file = "/Users/nelson.kanyali/Documents/dockertest/python/dialer/finance.log" #change this
dialer_name = "finance"   #this to be deprecated & passed via command
dialplan_target_extension = 999     #used as target in AMI Originate cmd #create function where you pass dialer name and get target, context, logfile
dialplan_context = "marketing_dialer"   #used as context in AMI Orignate cmd
start_calling_at = 7
stop_calling_at = 19