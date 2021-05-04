import socket
import logging
import subprocess
import threading
import time

class NetworkHandler:
    # Takes one string parameter: 'host' or 'client', default is 'host'
    def __init__(self, game: 'Game', machineType: str = 'host', resetting: bool = False):
        # Create class logger
        self.log = logging.getLogger("NetworkHandler")
        logging.getLogger().setLevel(logging.INFO)

        # Create game member variable
        self.game = game

        # Set timeout time to 10s
        socket.setdefaulttimeout(5)

        # Create exit flag for killing threads
        self.exitFlag = False

        # Input and Output ports
        self.iport = 10000
        self.oport = 10001
        
        # Member variables used for network setup
        self.machineType = machineType
        self.ipv4 = self.__getIPv4()

        # Setup netcode for either host or client
        if resetting == False:
            if machineType == 'client':
                self.log.info("Starting client setup...")
                self.__clientSetup()
                self.log.info("Completed client setup.")
            else:
                self.log.info("Starting host setup...")
                self.__hostSetup()
                self.log.info("Completed host setup.")
        else:
            self.log.info("Reset flag has been passed. Skipping connection attempts...")

        # Create listening thread
        self.listenThread = threading.Thread(target=self.listenLoop)
        self.log.info("Created listening thread.")
        

    # Sets up netcode for host machine
    def __hostSetup(self):
        # Create listening socket with iport
        self.isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.isock.bind((self.ipv4, self.iport))
        except OSError:
            self.log.info("ISOCK address already bound, continuing...")

        # Create command socket with oport
        self.osock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.osock.bind((self.ipv4, self.oport))
        except OSError:
            self.log.info("OSOCK address already bound, continuing...")


    # Sets up netcode for client machine
    def __clientSetup(self):
        self.hostipv4 = '192.168.1.6'
        
        # Create a TCP socket
        self.isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.osock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Grabs current IPv4
    def __getIPv4(self):
        # Get IPv4 with subprocess
        ipv4 = subprocess.check_output(['hostname', '--all-ip-addresses'])
        # This next line is for windows developement
        #ipv4 = socket.gethostbyname(socket.gethostname())
        # Convert to string and clean up, then return
        return ipv4.decode().strip()


    # Connects to either the host or client
    def connect(self):
        # Client connection setup
        if self.machineType == 'client':
            try: 
                self.log.info(f"Attempting to connect to host at {self.hostipv4}...")

                # Attempt to connect to host listen port to client command port
                #       use iport because the listen ports are the same on each device
                self.osock.connect((self.hostipv4, self.iport))
                self.log.info("\tConnected to host listen port.")

                # Adding a delay in connection to make sure other machine is ready
                time.sleep(0.5)
                
                # Attempt to connect to host command port to client command port
                #       use oport because the listen ports are the same on each device
                self.isock.connect((self.hostipv4, self.oport))
                self.log.info("\tConnected to host command port.")

                self.log.info("Successfully established TCP socket connection to host.")
                return True
            except socket.timeout:
                self.log.error(f"Connection to {self.hostipv4}:{self.port} timed out.")
            return False

        # Host connection setup
        else:
            try:
                self.log.info("Listening for client connection attempts...")

                # Listen for a connection attempt on the listen port
                self.isock.listen(1)
                # Establish connection to client command port
                self.iconnection, self.clientAddress = self.isock.accept()
                self.log.info("\tConnected to client command port.")

                # Listen for a connection attempt on the command port
                self.osock.listen(1)
                # Establish connection to client listen port
                self.oconnection, self.clientAddress = self.osock.accept()
                self.log.info("\tConnected to client listen port.")

                self.log.info("Successfully established TCP socket connection to client.")
                return True
            except:
                self.log.error("Failed to establish connection to client machine.")
            return False

    
    # Constantly listens on the isock
    def listenLoop(self):
        while self.exitFlag == False:
            received = self.receive(20)
            if received != None:
                received = received.decode()
                self.log.info(f"Received data: {received}")
                self.game.process(received)


    # Attempts to sends data to the other machine, can throw connection error
    def send(self, bytedata: bytes):
        if self.machineType == "host":
            self.oconnection.sendall(bytedata)
        else:
            self.osock.sendall(bytedata)
        self.log.info("Successfully sent data.")
    

    # Attempts to receive data from the established socket
    def receive(self, expectedBytes):
        try:
            if self.machineType == 'host':
                return self.iconnection.recv(expectedBytes)
            else:
                return self.isock.recv(expectedBytes)
        except:
            return None
        

    # sends a string to the other machine
    def strsend(self, strdata: str):
        self.send(strdata.encode())
        return True
