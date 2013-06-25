
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
    def read_response(self, timeout):
        '''Blocks until timeout reached, throws a ResponseTimeout if timeout
        is reached. If no timeout was passed then an endpoint-dependent
        default will be used'''
        pass

class ResponseTimeout(Exception):
    pass

class SocketEndpoint:

    SOCKET_TIMEOUT = 10.0
    socketlogging = False
    
    def __init__(self, config):

        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((config['address'], config['port']))
        self.buff = ''

        if config.has_key('promptstr'):
            self.promptstr = config['promptstr']
        else:
            self.promptstr = '>'
        if config.has_key('lineending'):
            self.lineending = config['lineending']
        else:
            self.lineending = '\r\n'

    def socket_log_sent(self, msg):
        if self.socketlogging:
            print('sock sent: ' + msg)

    def socket_log_recv(self, msg):
        if self.socketlogging:
            print('sock recv:' + msg)

    def put_cmd(self, cmd):
        # Expects devices to have to exhibit the following behavior:
        # CMD\r\n -> device
        # device -> CMD\r\n (echoed)
        # device -> prompt  (signifies ready for next command)
        sent = self._write_line(cmd)
        if sent == 0:
            raise RuntimeError('socket failed to send command.')
        echo = self._read_line(self.SOCKET_TIMEOUT)
        if not echo.strip().endswith(cmd):
            raise RuntimeError('expected terminal to echo command.')
        return sent

    def read_response(self, timeout=None):
        if timeout == None:
            timeout = self.SOCKET_TIMEOUT
        response = self._read_line(timeout)
        try:
            self._wait_for_prompt(self.SOCKET_TIMEOUT)
        except ResponseTimeout:
            raise RuntimeError('expected device to reply with telnet prompt')
        return response

    def _write_line(self, msg):
        msg_with_line = msg + self.lineending
        totalsent = 0
        while totalsent < len(msg_with_line):
            sent = self.sock.send(msg_with_line[totalsent:])
            self.socket_log_sent(msg_with_line[totalsent:])
            if sent == 0:
                raise RuntimeError('socket connection broken')
            totalsent += sent
        return totalsent

    def _wait_for_prompt(self, timeout):
        self._read_message(self.promptstr, timeout)

    def _read_line(self, timeout):
        return self._read_message(self.lineending, timeout)

    def _pop_buffer(self, delimiter):
        parts = self.buff.partition(delimiter)
        self.buff = parts[2]
        return parts[0]

    def _read_message(self, delimiter, timeout):
        '''reads a single line, or raises an error if a message was
        not received within a timeout, i.e. if the user expected a response
        from a non-response command.'''

        self.sock.settimeout(timeout)
        while True:
            if self.buff.count(delimiter) > 0:
                return self._pop_buffer(delimiter)
            try:
                msg = self.sock.recv(1024)
                self.socket_log_recv(msg)
                self.buff += msg
            except socket.timeout:
                raise ResponseTimeout()

Endpoint.register(SocketEndpoint)

def visa_log(msg):
    print('visa_simple: ' + msg)

VISA_USER_REQUEST = (1 << 6)
VISA_COMMAND_ERROR = (1 << 5)
VISA_EXEC_ERROR = (1 << 4)

class Instrument(object):

    def __init__(self, config):

        if config['type'] == 'socket':
            self.endp = SocketEndpoint(config)
        else:
            raise RuntimeError('unsupported instrument type')

        visa_log('Connection to device successfull')

        while True:
            try:
                visa_log(self.endp.read_response(1.0))
            except ResponseTimeout:
                break

        # Reset the device to a known state.
        # That state will be device dependent
        self.put_cmd('*RST')

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
        status = int(result)
        if status != 0:
            raise RuntimeError("error detected in visa command")
        #TODO: parse the errors, throw errors

