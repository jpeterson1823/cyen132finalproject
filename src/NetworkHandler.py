import logging, socket, subprocess


### TODO ######################################
# a. Test code
###############################################


class NetworkHandler:
    # Takes one string parameter: 'host' or 'client', default is 'host'
    def __init__(self, machineType: str = 'host', autoConnect: bool = False):
        # Used for logging
        self.__classStr = 'NetworkHandler: '
        
        # Member variables used for network setup
        self.machineType = machineType
        self.ipv4 = self.__getIPv4()
        self.port = 10000

        # Setup netcode for either host or client
        if machineType == 'client':
            logging.info(self.__classStr + "Starting client setup...")
            self.__clientSetup()
            logging.info(self.__classStr + "Completed client setup.")
        else:
            logging.info(self.__classStr + "Starting host setup...")
            self.__hostSetup()
            logging.info(self.__classStr + "Completed host setup.")
        
        # Attempt to connect to either host or client machine
        if autoConnect == True:
            logging.info(self.__classStr + "Starting automatic connection attempt...")
            if self.connect == False:
                logging.error(self.__classStr + "Connection to other machine failed to be established.")


    # Sets up netcode for host machine
    def __hostSetup(self):
        # Set timeout time to 10s
        socket.setdefaulttimeout(1)
        # Create TCP socket with timeout.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ipv4, self.port))


    # Sets up netcode for client machine
    def __clientSetup(self):
        # Get host's IPv4 from user input
        self.hostipv4 = input("Client setup initialized. Please enter the host's IPv4: ")
        while input("Entered IPv4: {hostipv4}\n Is this correct? (Y/n) ").lower() != 'y':
            self.hostipv4 = input("Please re-enter the host's IPv4: ")
        
        # Create a TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Grabs current IPv4
    def __getIPv4(self):
        # Get IPv4 with subprocess
        #ipv4 = subprocess.check_output(['hostname', '--all-ip-addresses'])
        ipv4 = socket.gethostbyname(socket.gethostname())
        # Convert to string and clean up, then return
        return ipv4.strip()


    # Connects to either the host or client
    def connect(self):
        # Client connection setup
        if self.machineType == 'client':
            try: 
                # Attempt to connect to host
                logging.info(self.__classStr + f"Attempting to connect to host at {self.hostipv4}:{self.port}...")
                self.socket.connect((self.hostipv4, self.port))
                logging.info(self.__classStr + "Successfully established TCP socket connection to host.")
                return True
            except socket.timeout:
                logging.error(self.__classStr + f"Socket.TimeoutError: Connection to {self.hostipv4}:{self.port} failed.")
            return False

        # Host connection setup
        else:
            try:
                # Listen for one new connection
                logging.info(self.__classStr + "Listening for client connection attempt...")
                self.socket.listen(0)
                # Establish connection to client
                self.connection, self.clientAddress = self.socket.accept()
                logging.info(self.__classStr + "Successfully established TCP socket connection to client.")
                return True
            except:
                logging.error(self.__classStr + "Failed to establish connection to client machine.")
            return False


    # Attempts to sends data to the other machine, can throw connection error
    def send(self, bytedata: bytes):
        logging.info(self.__classStr + "Attempting to send data...")
        self.connection.sendall(bytedata)
        logging.info(self.__classStr + "Successfully sent data.")
    

    # Attempts to receive data from the established socket
    def receive(self, expectedBytes):
        logging.info(self.__classStr + "Attempting to receive data...")
        try:
            if self.machineType == 'host':
                return self.connection.recv(expectedBytes).decode()
            else:
                return self.socket.recv(10).decode()
        except:
            logging.error(self.__classStr + "Failed to reveive data.")
            return None
        

    # sends a string to the other machine
    def strsend(self, strdata: str):
        try:
            self.send(strdata.encode())
            return True
        except:
            logging.error(self.__classStr + "Failed to send string data through TCP socket.")
        return False
