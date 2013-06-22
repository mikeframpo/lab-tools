
#endpoint base class stuff
from abc import ABCMeta, abstractmethod

#socketepoint stuff
import socket
import collections

class Endpoint:
    __metaclass__ = ABCMeta

    @abstractmethod
    def put_cmd(self, cmd):
        pass

    @abstractmethod
    def read_response(self):
        '''Blocks until timeout reached, returns None if nothing was read.'''
        pass

class SocketEndpoint:

    BUF_SIZE = 4096
    
    def __init__(self, address, port, timeout=1.0):
        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))
        self.sock.settimeout(timeout)
        self.buff = collections.deque(maxlen = self.BUF_SIZE)

    def put_cmd(self, cmd):
        sent = self._write_line(cmd)
        if sent == 0:
            #TODO: raise an error
            pass
        echo = self._read_line()
        if not echo.strip().endswith(cmd):
            raise RuntimeError('expected terminal to echo command.')
        return sent

    def read_response(self):
        return self._read_line()

    def _write_line(self, msg):
        msg_with_line = msg + '\r\n'
        totalsent = 0
        while totalsent < len(msg_with_line):
            sent = self.sock.send(msg_with_line[totalsent:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            totalsent += sent
        return totalsent

    def _buff_to_line(self):
        s = ''
        while True:
            try:
                c = self.buff.popleft()
                if c == '\n':
                    break
                s += c
            except IndexError:
                break
        return s

    def _read_line(self):
        '''reads a single line, or raises an error if a message was
        not received within a timeout, i.e. if the user expected a response
        from a non-response command.'''

        #TODO: block for half a second or so waiting for the first byte, but
        #       then only block for a few milliseconds waiting for the rest.
        if self.buff.count('\n') != 0:
            return self._buff_to_line()
        while True:
            timedout = False
            msg = ''
            try:
                msg = self.sock.recv(1024)
            except socket.timeout:
                timedout = True
            for c in msg:
                self.buff.append(c)
            if self.buff.count('\n') != 0:
                return self._buff_to_line()
            if timedout:
                return None

Endpoint.register(SocketEndpoint)

def visa_log(msg):
    print('visa_simple: ' + msg)

VISA_USER_REQUEST = (1 << 6)
VISA_COMMAND_ERROR = (1 << 5)
VISA_EXEC_ERROR = (1 << 4)

class Instrument(object):

    #TODO: change the method definition to parse a SCPI string
    def __init__(self, address, port):

        self.endp = SocketEndpoint(address, port)
        visa_log('Connection to device successfull')

        line = self.endp.read_response()
        while line != None:
            print(line)
            line = self.endp.read_response()

        # Reset the device to a known state.
        self.put_cmd('*RST')

        self.put_cmd('*IDN?')
        idn = self.read_response()
        if idn != None:
            visa_log(idn)
        else:
            visa_log('Failed to read device IDN')

        # enable device errors to be reported
        # TODO: make this settable by passing in a device-config
        error_settings = '*ESE ' + str(VISA_USER_REQUEST | VISA_COMMAND_ERROR
                                    | VISA_EXEC_ERROR)
        self.put_cmd(error_settings)

    def put_cmd(self, cmd):
        '''Send the command to the device, do not attempt to read a result.'''
        self.endp.put_cmd('*CLS')
        self.endp.put_cmd(cmd)

    def read_response(self):
        response = self.endp.read_response()
        self.check_errors()
        return response

    def check_errors(self):
        self.endp.put_cmd('*ESR?')
        result = self.endp.read_response()
        if result != None:
            status = int(result)
            if status != 0:
                raise RuntimeError("error detected in visa command")
            #TODO: parse the errors, throw errors

