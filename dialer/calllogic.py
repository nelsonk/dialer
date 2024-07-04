import configparser
import socket
import time
import functools
import sys

from datetime import datetime, timedelta

#imports from project
from dialer.database.dbWork import dbWork
from dialer.database.models import Db


#seperate imports and method with 2 lines
def timerDecorator(func):
    @functools.wraps(func)
    def decorate(args):
        print("Testing Decorator")
        func()
        print("Ending testing Decorator")
    return decorate


class Call:
    def __init__(self):
        self.logfile = "/Users/nelson.kanyali/Documents/dockertest/python/dialer/finance.log" #change this
        self.base_date = datetime(2024, 5, 26) #change this, start date for compaign
        self.dialer = "finance"
        config = configparser.ConfigParser()
        config.read('database.ini')
        self.counter = 0
        self.sock = None
        self.amiUsername = config['ami']['username']
        self.amiPassword = config['ami']['password']
        self.amiPort = config['ami']['port']
        self.amiServer = config['ami']['server']
        self.target = 999
        self.context = "marketing_dialer"

    def checkTime(self, task):
        current_time = datetime.now().hour
        if task == "call" and current_time > 19 and current_time < 7:
            print("Not allowed to run at this time")
            sys.exit(1)
        elif task == "file" and current_time < 22 and current_time > 7:
            print("Not allowed to run at this time")
            sys.exit(1)
        else:
            pass

    #@timerDecorator
    def readFile(self):
        with open(self.logfile, 'r') as file:
            for line in file:
                self.checkTime("file")
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
                    dbWork().finalUpdate(number[-9:], self.dialer, run_on)
                elif int(duration) > 10:
                    dbWork().finalUpdate(number[-9:], self.dialer)
                else:
                    print(f"failed call atempt for {number[-9:]}, not updating DB")
                self.counter += 1
        return print(f"{self.counter} records updated")

    def establishSocket(self):
        try:
            self.sock = socket.create_connection((self.amiServer, self.amiPort))
            # Prepare authentication request
            authenticationRequest = (
                "Action: Login\r\n"
                f"Username: {self.amiUsername}\r\n"
                f"Secret: {self.amiPassword}\r\n"
                "Events: off\r\n\r\n"
            )
            self.sock.sendall(authenticationRequest.encode())
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

    def initiateCall(self,orignateRequests, retry=0):
        ourRequest = orignateRequests
        try:
            self.sock.sendall(ourRequest.encode())
            time.sleep(1)
            orignateResponse = self.sock.recv(4096).decode()
            if "Success" in orignateResponse:
                return "Successful"
            else:
                if retry < 3:
                    print("Failed to initiate call, trying again")
                    return self.initiateCall(ourRequest, retry + 1)
        except socket.timeout:
            if retry < 3:
                print(f"Failed to send Originate request, Socket Timed out")
                return self.initiateCall(ourRequest, retry + 1)
        except socket.error as e:
            if retry < 3:
                print(f"Failed to send Originate request, Socket send error: {e}")
                return self.initiateCall(ourRequest, retry + 1)
        return "Maximum retries reached, call origination failed"

    #@timerDecorator
    def call(self):
        records = dbWork().get()
        status = self.establishSocket()
        print(status)
        if status == "Connected":
            for record in records:
                self.checkTime("call")
                recordId = record["id"]
                recordNumber = str(record["number"])
                recordLanguage = record["language"]
                recordLevel = record["level"]
                recordType = record["type"]
                mychannel = f"Local/0{recordNumber[-9:]}@from-internal"

                #Prepare originate request
                originateRequest = (
                    "Action: Originate\r\n"
                    f"Channel: {mychannel}\r\n"
                    f"Variable: clid=0{recordNumber[-9:]}\r\n"
                    f"Variable: dialer={self.dialer}\r\n"
                    f"Variable: language={recordLanguage}\r\n"
                    f"Variable: level={recordLevel}\r\n"
                    f"Variable: type={recordType}\r\n"
                    "Callerid: \r\n"
                    f"Exten: {self.target}\r\n"
                    f"Context: {self.context}\r\n"
                    "Priority: 1\r\n"
                    "Async: true\r\n\r\n"
                )
                self.initiateCall(originateRequest)
                if int(recordLevel) > 0:
                    dbWork().initialUpdate(recordId)
                self.counter += 1
                time.sleep(10)
            self.sock.close()
            return print(f"{self.counter} numbers called")


if __name__ == "__main__":
    search = False
    call = Call()
    if len(sys.argv) > 1:
        call.readFile()
    else:
        call.call()   
    Db.close()
    sys.exit(0)
