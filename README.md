This system automates calls to customers throughout a campaign, scheduling diferent trainings per week depending on which level customer is on. Human intervention is only needed on initial upload of numbers.

It involves using peewee to manage all database interactions, sockets for connection to Asterisk via AMI port to initiate calls, and reading a log file written by Asterisk to reschedule customer for another training or same training depending on whether they listened to previous training for at least a specified number of seconds.

Key Components:
- A front end system uploads numbers to a tmp csv file on server, file has column for phone number, language and type of campaign
- Has an dialer/upload.py file which is called with tmp file and name of dialer and it uploads numbers to database
- dialer/calllogic.py used for initiating calls and updating database to reschedule training. It is also used to read log file and reschedule training. If you run it without an argument, it calls numbers from DB else, it reads file & updates DB
- DB models are defined in dialer/model.py, reading login details from database.ini using configParser
- All interactions with DB using peewee are defined in dialer/dbWork.py