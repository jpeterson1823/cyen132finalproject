import logging, socket, subprocess


### TODO ######################################
# a. Finish the receive function              #
###############################################


class NetworkHandler:
    # Takes one string parameter: 'host' or 'client', default is 'host'
    def __init__(self, machineType: str = 'host'):
        self.machineType = machineType
        self.ipv4 = self.__getIPv4()
        self.port = 10000

        # Setup netcode for either host or client
        if machineType == 'client':
            logging.info("Starting client setup...")
            self.__clientSetup()
            logging.info("Completed client setup.")
        else:
            logging.info("starting host setup...")
            self.__hostSetup()
            logging.info("Completed host setup.")
        
        # Attempt to connect to either host or client machine
        if self.__connect == False:
            logging.info("CONNECITON FAILED TO BE ESTABLISHED. EXITING.....")
            exit(1)

    # Sets up netcode for host machine
    def __hostSetup(self):
        # Create TCP socket with default timeout of 10s
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(10)
        socket.bind((self.ipv4, self.port))

    # Sets up netcode for client machine
    def __clientSetup(self):
        # Get host's IPv4 from user input
        self.hostipv4 = input("Client setup initialized. Please enter the host's IPv4: ")
        while input("Entered IPv4: {hostipv4}\n Is this correct? (Y/n) ").lower() != 'y':
            self.hostipv4 = input("Please re-enter the host's IPv4: ")
        
        # Create a TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connects to either the host or client
    def __connect(self):
        # Client connection setup
        if self.machineType == 'client':
            try: 
                # Attempt to connect to host
                logging.info(f"Attempting to connect to host at {self.hostipv4}:{self.port}...")
                self.socket.connect((self.hostipv4, self.port))
                logging.info("Successfully established TCP socket connection to host.")
                return True
            except socket.timeout:
                logging.info(f"Socket.TimeoutError: Connection to {self.hostipv4}:{self.port} failed.")
            return False

        # Host connection setup
        else:
            try:
                # Listen for one new connection
                logging.info("Listening for client connection attempt...")
                self.socket.listen(0)
                # Establish connection to client
                self.connection, self.clientAddress = self.socket.accept()
                logging.info("Successfully established TCP socket connection to client.")
                return True
            except:
                logging.info("Connection Error: failed to establish connection to client machine.")
            return False


    # Grabs current IPv4
    def __getIPv4(self):
        # Get IPv4 with subprocess
        ipv4 = subprocess.check_output(['hostname', '--all-ip-addresses'])
        # Convert to string and clean up, then return
        return ipv4.decode().strip()

    # Attempts to sends data to the other machine, can throw connection error
    def send(self, bytedata: bytes):
        self.connection.sendall(bytedata)
    
    # Attempts to receive data from the established socket
    def receive(self):
        pass

    # sends a string to the other machine
    def strsend(self, strdata: str):
        try:
            self.send(strdata.encode())
            return True
        except:
            logging.info("TCPDataError: Failed to send string data through TCP socket.")
        return False
