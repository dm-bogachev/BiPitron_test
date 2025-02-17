import socket
import logging
from RobotConfig import RobotConfig

logger = logging.getLogger()

class RobotConnection:
    def __init__(self):
        self.__config = RobotConfig()
        self.__tcp_attempts = 0
        self.connected = False
        
    def connect(self):
        logger.info(f'Start socket initialization')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.__config['host'], self.__config['port']))
        s.listen()
        logger.info(f'Socket is in listening state on {self.__config["host"]}:{self.__config["port"]}')
        try:
            self.connection, ip_address = s.accept()
        except socket.timeout:
            logger.warning('Socket accept timed out')
            return
        self.connection.settimeout(self.__config['timeout'])
        logger.info(f'Robot with IP {ip_address} was connected')
        self.connected = True

    def disconnect(self):
        if self.connected:
            self.connection.close()
            self.connected = False
            logger.info('Robot disconnected')

    def send(self, request):
        try:
            self.connection.sendall(request.encode("UTF-8"))
            logger.debug(f'Sent data: {request}')
        except socket.timeout:
            self.handle_timeout()
        self.__tcp_attempts = 0

    def receive(self):
        try:
            response = self.connection.recv(1024)
        except socket.timeout:
            self.handle_timeout()
            return None
        self.__tcp_attempts = 0
        logger.debug(f'Received data: {response}')
        return response

    def handle_timeout(self):
        logger.error('Connection timeout')
        self.__tcp_attempts += 1
        if self.__tcp_attempts >= self.__config['max_tcp_attempts']:
            logger.error('Max TCP attempts reached')
            self.disconnect()