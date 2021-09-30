# Macro definitions used by the server and clients.

# Debug mode.
DEBUG_MODE = True

# Plugins.
VIFC = False

# Constants.
HOST = "localhost"
SERVER_PORT = 50051
SERVER_CERTIFICATE = "tls_certificates/server.crt"
SERVER_KEY = "tls_certificates/server.key"
PACKETIN_IFACE = "enp0s3"
PACKETOUT_IFACE = "s1-eth1"

def print_debug(str):
    if DEBUG_MODE:
        print str
