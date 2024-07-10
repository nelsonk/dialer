Auto-Training Dialer

Automate customer trainings over the phone with no human intervention.


Overview:

This system automates calls to customers throughout a campaign, scheduling diferent trainings per week depending on which level customer is on. Human intervention is only needed on initial upload of numbers.

It involves using peewee to manage all database interactions, sockets for connection to Asterisk via AMI port to initiate calls, and reading a log file written by Asterisk to reschedule customer for another training or same training depending on whether they listened to previous training for at least a specified number of seconds.


Requirements:
- python 3.6+


Installation:

- pip install peewee
- pip install pymysql

- Have your frontend application upload .csv file with columns in this order; phone_number, customer_language, campaign_type
    - training_level of 0 is auto assigned on initial upload
    - First row is ignored, assumed to be for column names even though they're optional

- Have your application execute this script with full path to location of uploaded file and name of autodialer
    - The uploaded file is meant to be deleted by this script after reading it, make sure parent folder has (wx) permissions

        Example:

        /usr/bin/python3 upload.py $tmpFilePath $dialer_name

    - This script will read numbers from csv and upload to database.

- Create cronjob that executes the calling script at top of hour to call all customers scheduled for that day that hour

    0 7-18 * * * /usr/bin/python3 calllogic.py call dialer_name

    - Calls are only initiatied from 7am to 7pm. 

- Create a cronjob that runs script that checks log file to see if a number was called and listened to a training recording for at least a specific number of seconds

    0 22 * * * /usr/bin/python3 calllogic.py update dialer_name


AMI & Database:
- Add your database and AMI credentials in database.ini file
- If these scripts are not running on same server having AMI & DB, make sure remote access is allowed.
- Variables; clid (phone_number), dialer (name of autodialer), language, level (level of training whose recordings you should play, 0 is for week recording about when customer wants to be called), type (type of campaign incase one dialer is used for multiple campaigns)


Settings:
Go to configs/seetings.py to make changes to settings like:
- Time frame script is allowed to call customers
- Path to asterisk_log file
- When campaign is supposed to start, this determines when customer calls are to be scheduled
- You dialplan context & target where customer calls are supposed to sent on pickup, which should contain the logic for playing recordings etc

