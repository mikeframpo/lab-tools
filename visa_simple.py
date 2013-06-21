

# **** Design overview ****
# 
# Objective:
#   to create a visa-like interface for scpi commands
#   this will be used primarily for driving agilent instruments
#
# class Instrument:
#   defines the normal interface for communicating with a device
#   instanciated by passing a visa string into the constructor
#   handles errors in a nice way
#   provides a simple interface, write_cmd(), query_cmd()
#
# class Endpoint:
#   abstract base class specifying the low level commands
#
# class SocketEndpoint:
#   endpoint for a network socket.
#
# class SCPIError:
#   

#telnet interface stuff
import telnetlib

#endpoint base class stuff
from abc import ABCMeta, abstractmethod

#socketepoint stuff
import telnetlib

class Endpoint:
    __metaclass__ = ABCMeta

    @abstractmethod
    def put_cmd(self, s):
        pass

    @abstractmethod
    def read_available(self):
        pass

class TelnetEndpoint:
    
    def __init__(self, address, port, timeout):
        self.telnet = telnetlib.Telnet(address, port, timeout)

    def put_cmd(self, cmd):
        self.telnet.write(cmd + "\n")
        response_raw = self.telnet.read_some()
        response = ""
        if len(response_raw) == 0:
            raise RuntimeError("command returned non-zero response")
        elif not response_raw.startswith(cmd):
            raise RuntimeError("expected device to echo command")
        response = response_raw.lstrip(cmd)
        return response
    
    def read_available(self):
        return self.telnet.read_some()


Endpoint.register(TelnetEndpoint)

def visa_log(msg):
    print("visa_simple: " + msg)

VISA_USER_REQUEST = (1 << 6)
VISA_COMMAND_ERROR = (1 << 5)
VISA_EXEC_ERROR = (1 << 4)

class Instrument:

    #TODO: change the method definition to parse a SCPI string
    def __init__(self, address, port):

        self.endp = TelnetEndpoint(address, port, 2)
        visa_log("Connection to device successfull")

        idn = self.put_cmd("*IDN?")
        if idn != None:
            visa_log(idn)
        else:
            visa_log("Failed to read device IDN")

        # enable device errors to be reported
        # TODO: make this settable by passing in a device-config
        self.put_cmd("*ESE=" + 
            str(VISA_USER_REQUEST |
            VISA_COMMAND_ERROR |
            VISA_EXEC_ERROR))

    def put_cmd(self, cmd):
        """Send the command to the device, do not attempt to read a result."""
        self.endp.put_cmd("*CLS")
        response = self.endp.put_cmd(cmd)
        self.check_errors()
        #TODO: parse the reponse
        return response

    def check_errors(self):
        self.endp.write_str("*ESR?")
        result = self.endp.read_str()
        if result != None:
            status = int(result)
            #TODO: parse the errors, throw errors
        #throw an error if nothing returned

siggen = Instrument("132.181.52.71", 5024)
siggen.put_cmd("NOTCOMMAND")

