import socket
import time
import functools
import sys

from datetime import datetime, timedelta

#imports from project
from dialer.database.dbwork import DbWork
#from dialer.settings import *
import dialer.settings as settings


#seperate imports and class with 2 lines
def timer_decorator(func):
    @functools.wraps(func)
    def decorate(args):
        print("Testing Decorator")
        func()
        print("Ending testing Decorator")
    return decorate


class Call:
    def __init__(self):
        self.log_file = settings.asterisk_log_file
        self.base_date = settings.campaign_starts_on
        self.dialer = settings.dialer_name
        self.counter = 0
        self.sock = None
        self.ami_username = settings.ami_username
        self.ami_password = settings.ami_password
        self.ami_port = settings.ami_port
        self.ami_server = settings.ami_server
        self.extension = settings.dialplan_target_extension
        self.context = settings.dialplan_context
        self.closing_time = settings.stop_calling_at
        self.opening_time = settings.start_calling_at

    def check_time(self, task):
        current_time = datetime.now().hour
        if task == "call" and current_time > self.closing_time or current_time < self.opening_time:
            print("Not allowed to run at this time")
            sys.exit(1)
        else:
            pass

    #@timer_decorator
    def read_file(self):
        with open(self.log_file, 'r') as file:
            for line in file:
                self.check_time("file")
                values = [value.strip() for value in line.strip().split(',')]
                day = None
                time = None
                try:
                    number = values[0]
                    duration = values[1]
                    day = int(values[2])
                    time = values[3]
                except:
                    pass
                if day is not None and time is not None:
                    delta = timedelta(days=day)
                    new_date = (self.base_date + delta).date()
                    run_on = f"{new_date} {time}:00:00"
                    DbWork().final_update(number[-9:], self.dialer, run_on)
                elif int(duration) > 10:
                    DbWork().final_update(number[-9:], self.dialer)
                else:
                    print(f"failed call atempt for {number[-9:]}, not updating DB")
                self.counter += 1
        return print(f"{self.counter} records updated")

    def establish_socket(self):
        try:
            self.sock = socket.create_connection((self.ami_server, self.ami_port))
            # Prepare authentication request
            authentication_request = (
                "Action: Login\r\n"
                f"Username: {self.ami_username}\r\n"
                f"Secret: {self.ami_password}\r\n"
                "Events: off\r\n\r\n"
            )
            self.sock.sendall(authentication_request.encode())
            time.sleep(0.2)
            response = self.sock.recv(4096).decode()
            if 'Success' in response:
                status = "Connected"
            else:
                status = "Could not authenticate"              
        except socket.timeout:
            status = "Socket send timed out"
        except socket.error as e:
            status = f"Socket send error: {e}"
        return status

    def initiate_call(self,orignate_requests, retry=0):
        our_request = orignate_requests
        try:
            self.sock.sendall(our_request.encode())
            time.sleep(1)
            orignate_response = self.sock.recv(4096).decode()
            if "Success" in orignate_response:
                return "Successful"
            else:
                if retry < 3:
                    print("Failed to initiate call, trying again")
                    return self.initiate_call(our_request, retry + 1)
        except socket.timeout:
            if retry < 3:
                print(f"Failed to send Originate request, Socket Timed out")
                return self.initiate_call(our_request, retry + 1)
        except socket.error as e:
            if retry < 3:
                print(f"Failed to send Originate request, Socket send error: {e}")
                return self.initiate_call(our_request, retry + 1)
        return "Maximum retries reached, call origination failed"

    #@timerDecorator
    def call(self):
        records = DbWork().get()
        status = self.establish_socket()
        print(status)
        if status == "Connected":
            for record in records:
                self.check_time("call")
                record_id = record["id"]
                record_number = str(record["number"])
                record_language = record["language"]
                record_level = record["level"]
                record_type = record["type"]
                my_channel = f"Local/0{record_number[-9:]}@from-internal"

                #Prepare originate request
                originate_request = (
                    "Action: Originate\r\n"
                    f"Channel: {my_channel}\r\n"
                    f"Variable: clid=0{record_number[-9:]}\r\n"
                    f"Variable: dialer={self.dialer}\r\n"
                    f"Variable: language={record_language}\r\n"
                    f"Variable: level={record_level}\r\n"
                    f"Variable: type={record_type}\r\n"
                    "Callerid: \r\n"
                    f"Exten: {self.extension}\r\n"
                    f"Context: {self.context}\r\n"
                    "Priority: 1\r\n"
                    "Async: true\r\n\r\n"
                )
                self.initiate_call(originate_request)
                if int(record_level) > 0:
                    DbWork().initial_update(record_id)
                self.counter += 1
                time.sleep(10)
            self.sock.close()
            return print(f"{self.counter} numbers called")


if __name__ == "__main__":
    search = False
    call = Call()
    if len(sys.argv) > 1:
        call.read_file()
    else:
        call.call()   
    settings.Db.close()
    sys.exit(0)
