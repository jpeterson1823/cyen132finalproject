import socket
import logging
import subprocess
import threading

class NetworkHandler:
    # Takes one string parameter: 'host' or 'client', default is 'host'
    def __init__(self, game: 'Game', machineType: str = 'host', autoConnect: bool = False):
        self.game = game

        # Create exit flag for killing threads
        self.exitFlag = False

        # Used for logging
        self.__classStr = 'NetworkHandler: '

        # Input and Output ports
        self.iport = 10000
        self.oport = 10001
        
        # Member variables used for network setup
        self.machineType = machineType
        self.ipv4 = self.__getIPv4()

        # Setup netcode for either host or client
        if machineType == 'client':
            logging.info(self.__classStr + "Starting client setup...")
            self.__clientSetup()
            logging.info(self.__classStr + "Completed client setup.")
        else:
            logging.info(self.__classStr + "Starting host setup...")
            self.__hostSetup()
            logging.info(self.__classStr + "Completed host setup.")

        # Create listening thread
        self.listenThread = threading.Thread(target=self.listenLoop)
        logging.info(self.__classStr + "Created listening thread.")
        

    # Sets up netcode for host machine
    def __hostSetup(self):
        # Set timeout time to 10s
        #socket.setdefaulttimeout(10)

        # Create listening socket with iport
        self.isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isock.bind((self.ipv4, self.iport))

        # Create command socket with oport
        self.osock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.osock.bind((self.ipv4, self.oport))


    # Sets up netcode for client machine
    def __clientSetup(self):
        # Get host's IPv4 from user input
        self.hostipv4 = input("Client setup initialized. Please enter the host's IPv4: ")
        while input(f"Entered IPv4: {self.hostipv4}\n Is this correct? (Y/n) ").lower() != 'y':
            self.hostipv4 = input("Please re-enter the host's IPv4: ")
        
        # Create a TCP socket
        self.isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.osock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Grabs current IPv4
    def __getIPv4(self):
        # Get IPv4 with subprocess
        #ipv4 = subprocess.check_output(['hostname', '--all-ip-addresses'])
        # This next line is for windows developement
        ipv4 = socket.gethostbyname(socket.gethostname())
        # Convert to string and clean up, then return
        return ipv4.strip()


    # Connects to either the host or client
    def connect(self):
        # Client connection setup
        if self.machineType == 'client':
            try: 
                logging.info(self.__classStr + f"Attempting to connect to host at {self.hostipv4}...")

                # Attempt to connect to host listen port to client command port
                #       use iport because the listen ports are the same on each device
                self.osock.connect((self.hostipv4, self.iport))
                logging.info(self.__classStr + "\tConnected to host listen port.")
                
                # Attempt to connect to host command port to client command port
                #       use oport because the listen ports are the same on each device
                self.isock.connect((self.hostipv4, self.oport))
                logging.info(self.__classStr + "\tConnected to host command port.")

                logging.info(self.__classStr + "Successfully established TCP socket connection to host.")
                return True
            except socket.timeout:
                logging.error(self.__classStr + f"Connection to {self.hostipv4}:{self.port} timed out.")
            return False

        # Host connection setup
        else:
            try:
                logging.info(self.__classStr + "Listening for client connection attempts...")

                # Listen for a connection attempt on the listen port
                self.isock.listen(1)
                # Establish connection to client command port
                self.iconnection, self.clientAddress = self.isock.accept()
                logging.info(self.__classStr + "\tConnected to client command port.")

                # Listen for a connection attempt on the command port
                self.osock.listen(1)
                # Establish connection to client listen port
                self.oconnection, self.clientAddress = self.osock.accept()
                logging.info(self.__classStr + "\tConnected to client listen port.")

                logging.info(self.__classStr + "Successfully established TCP socket connection to client.")
                return True
            except:
                logging.error(self.__classStr + "Failed to establish connection to client machine.")
            return False

    
    # Constantly listens on the isock
    def listenLoop(self):
        while self.exitFlag == False:
            received = self.receive(20)
            if received != None:
                received = received.decode()
                logging.info(self.__classStr + f"Received data: {received}")
                self.game.processData(received)


    # Attempts to sends data to the other machine, can throw connection error
    def send(self, bytedata: bytes):
        if self.machineType == "host":
            self.oconnection.sendall(bytedata)
        else:
            self.osock.sendall(bytedata)
        logging.info(self.__classStr + "Successfully sent data.")
    

    # Attempts to receive data from the established socket
    def receive(self, expectedBytes):
        #try:
        if self.machineType == 'host':
            return self.iconnection.recv(expectedBytes)
        else:
            return self.isock.recv(expectedBytes)
        #except:
        #    return None
        

    # sends a string to the other machine
    def strsend(self, strdata: str):
        self.send(strdata.encode())
        return True
