
# Auto-Training Dialer

Automate customer trainings over the phone with no human intervention.
## Authors

- [Nelson Kanyali](https://github.com/nelsonk)


## Overview
This system automates calls to customers throughout a campaign, scheduling diferent trainings per week depending on which level customer is on. Human intervention is only needed on initial upload of numbers.

It involves using peewee to manage all database interactions, sockets for connection to Asterisk via AMI port to initiate calls, and reading a log file written by Asterisk to reschedule customer for another training or same training depending on whether they listened to previous training for at least a specified number of seconds.
## Features

- Upload customer campaign details to database
- Auto call customers
- Redirect customer call to a custom asterisk dialplan to play training audio
- Move customer through the training modules depending on whether they successfully listened to previous module


## Installation

Requirements:
```
  python 3.6+
```

Install package:
```bash
pip install dialer
```

Post installation script:

Run post install setup script from a directory from which you will be running all usage commands, from now on, we shall refer to this folder as ```root_folder```.
```bash
dialer_setup dialer_name
```
- Change ```dialer_name``` to the name for the autodialer. This same name should be used on all usage commands.
- This will create a settings.py file and database/database.ini and logs/asterisk_```dialer_name``` in this ```root_folder```
- It will also add cronjobs to run calling feature at top of every hour from 7am to 9pm. Runs script to update DB using asterisk_dialer_name.log at 10pm. You may edit it in your crontab
- The calling script doesn't call customers who have taken 4 or more consecutive weeks without picking our calls
- You can run command again in same ```root_folder``` with different dialer_name to setup another autodialer.

Asterisk AMI & Database:

- Add your database and AMI credentials to ```root_folder```/database/database.ini file


Settings:

Go to ```root_folder```/settings.py to make changes to settings like:

- Time frame script is allowed to call customers
- When campaign is supposed to start, this determines when customer calls are to be scheduled
- You dialplan context & target where customer calls are supposed to be sent on pickup, which should contain the logic for playing recordings etc


## Usage/Examples

Have your frontend application upload .csv file with columns in this order; phone_number, customer_language, campaign_type.

- Training_level of 0 is auto assigned on initial upload
- First row is ignored, assumed to be for column names even though they're optional

Have your application execute this command with full path to uploaded file and ```dialer_name``` used at setup.

- The uploaded file is meant to be deleted by this script after reading it, make sure parent folder has (wx) permissions.
Command:

```bash
cd root_folder && upload_to_dialer dialer_name full_path_csv_file.csv
```

- This script will read numbers from csv and upload to database.

## Asterisk Setup

- Variables; ```clid``` (phone_number), ```dialer``` (name of autodialer), ```language``` (customer language), ```level``` (level of training whose recordings you should play, 0 is for recording about when customer wants to be called), ```type``` (type of campaign incase one dialer is used for multiple campaigns) shall be sent on the AMI Orignate request, use them in your asterisk custom dialplan
- Set your asterisk custom dialplan to write to ```root_folder```/logs/asterisk_```dialer_name```.log on call hangup, in this format;

    ```phone_number```, ```duration_of_call``` (in seconds), ```day_they_prefer_to_be_called``` (i.e 1 for Monday, 2 for Tue etc), ```time_they_prefer_to_be_called``` (i.e 8 for 8am, 14 for 2pm)

    Example: ```259790551930, 40, 3, 13```

- The last two should only be written at the beginning when customers are choose when to be called.
