
class Connection():

    CLIENT_CONNECTED = 1
    CLIENT_AUTHENTICATED = 2

    def __init__(self, user):
        self.user = user
        self.state = Connection.CLIENT_CONNECTED
        self.packet_in_buffer = []
