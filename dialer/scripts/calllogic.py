#!/usr/bin/env python3

import argparse
import socket
import sys
import time
from datetime import datetime, timedelta

from dialer.configs import logger
from dialer.configs import settings
from dialer.database.dbwork import DbWork
from dialer.handlers import files

log = logger.get_logger()


class Call:
    """
    Class to handling calling and updating database
    """
    def __init__(self, dialer_name):
        self.dialer = dialer_name #required parameters first & seperate

        self.counter = 0
        self.log_file = settings.get_dialer_specific_configs(self.dialer)['asterisk_log_file']
        self.sock = None

    def check_time(self, task):
        """
        Check time
        """
        current_time = datetime.now().hour

        if (task == "call" and 
            current_time > settings.STOP_CALLING_AT or 
            current_time < settings.START_CALLING_AT):
            log.error("Not allowed to run at this time")
            sys.exit(1)

    def read_file(self):
        """
        Read asterisk logfile and schedule customer for next training module or a retry
        """
        for values in files.Read().get_list_from(self.log_file):
            day_selected = None
            time_selected = None

            try:
                number = values[0]
                duration = values[1]
                day_selected = int(values[2])
                time_selected = values[3]
            except (IndexError, ValueError) as e:
                log.exception("Optional Execption %s while reading %s file", e, self.log_file)

            if day_selected is not None and time_selected is not None:
                new_date = (settings.campaign_starts_on + timedelta(days=day_selected)).date()
                run_on = f"{new_date} {time_selected}:00:00"
                DbWork().final_update(number, self.dialer, run_on)
            elif int(duration) > 10:
                DbWork().final_update(number, self.dialer)
            else:
                log.warning("failed call atempt for %s, not updating DB", number)

            self.counter += 1

        return log.info("%s records updated", self.counter)

    def establish_socket(self):
        """
        Establish socket connection to Asterisk AMI server
        """
        try:
            self.sock = socket.create_connection((settings.ami_server, settings.ami_port))

            authentication_request = (
                "Action: Login\r\n"
                f"Username: {settings.ami_username}\r\n"
                f"Secret: {settings.ami_password}\r\n"
                "Events: off\r\n\r\n"
            )
            self.sock.sendall(authentication_request.encode())
            time.sleep(0.2)

            if 'Success' in self.sock.recv(4096).decode():
                return "Connected"  
                     
            log.error("AMI socket establishment failed: Could not authenticate")
            return "Could not authenticate"
        
        except socket.timeout:
            log.error("AMI socket establishment failed: Socket send timed out")
            return "Socket send timed out"  
              
        except socket.error as e:
            log.error("AMI socket establishment: Socket send error %s",e)
            return "Socket send error: %s", e

    def initiate_call(self,orignate_requests, retry=0):
        """
        Send Orignate request to AMI
        """
        try:
            self.sock.sendall(orignate_requests.encode())
            time.sleep(1)
            orignate_response = self.sock.recv(4096).decode()

            if "Success" in orignate_response:
                return "Successful"
            
            if retry < 3:
                log.warning("Failed to initiate call, trying again")
                return self.initiate_call(orignate_requests, retry + 1)
            
        except socket.timeout:
            if retry < 3:
                log.warning("Failed to send Originate request, Socket Timed out")
                return self.initiate_call(orignate_requests, retry + 1) 
                       
        except socket.error as e:
            if retry < 3:
                log.warning("Failed to send Originate request, Socket send error: %s", e)
                return self.initiate_call(orignate_requests, retry + 1)
            
        return log.error("Maximum retries reached, call origination failed")

    def call(self):
        """
        Where all calling logic comes together
        """
        if self.establish_socket() == "Connected":
            for record in DbWork().get(self.dialer):
                self.check_time("call")

                my_channel = f"Local/{str(record["phone_number"])}@from-internal"
                originate_request = (
                    "Action: Originate\r\n"
                    f"Channel: {my_channel}\r\n"
                    f"Variable: clid={str(record["phone_number"])}\r\n"
                    f"Variable: dialer={self.dialer}\r\n"
                    f"Variable: language={record["customer_language_name"]}\r\n"
                    f"Variable: level={record["training_level"]}\r\n"
                    f"Variable: type={record["campaign_type"]}\r\n"
                    "Callerid: \r\n"
                    f"Exten: {settings.DIALPLAN_TARGET_EXTENSION}\r\n"
                    f"Context: {settings.DIALPLAN_CONTEXT}\r\n"
                    "Priority: 1\r\n"
                    "Async: true\r\n\r\n"
                )
                log.debug("Originate Request: %s", originate_request)

                self.initiate_call(originate_request)

                if int(record["training_level"]) > 0:
                    DbWork().initial_update(record["id"], record["retry_on"], record["run_on"])

                self.counter += 1
                time.sleep(10)

            self.sock.close()
            log.info("%s numbers called", self.counter)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dialer", help="Specify name of autodialer as one word i.e overdue")
    parser.add_argument("-c", "--call", 
                        help="To invoke calling feature otherwise it will read asterisk log file", 
                        action="store_true")

    call = Call(parser.parse_args().dialer)

    if parser.parse_args().call:
        call.call()           
    else:
        call.read_file()

    settings.Db.close()
    log.info("Script's job is done, exiting")
    sys.exit(0)


if __name__ == "__main__":
    main()
