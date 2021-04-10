import socket, subprocess

class NetworkHandler:
    def __init__(self):
        pass

    def hostSetup(self):
        pass

    def clientSetup(self):
        pass

    # Grabs current IPv4
    def __getIPv4(self):
        # Get IPv4 with subprocess
        ipv4 = subprocess.check_output(['hostname', '--all-ip-addresses'])
        # Convert to string and clean up, then return
        return ipv4.decode().strip()
