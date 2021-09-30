import grpc
import struct

from p4.v1 import p4runtime_pb2 as p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc as p4runtime_pb2_grpc
from protobuffs import auth_pb2 as auth_pb2

from config import ServerConfig

from scapy.all import *
from binascii import hexlify

from time import sleep

import sys

class P4RuntimeClient():

    def __init__(self):
        # Configure the host and the port to which the client should connect to.
        self.host = ServerConfig.HOST
        self.server_port = ServerConfig.SERVER_PORT

        with open(ServerConfig.SERVER_CERTIFICATE, "rb") as file:
            trusted_certs = file.read()

        # Instantiate a communication channel and bind the client to the server.
        self.credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        self.channel = grpc.secure_channel("{}:{}".format(self.host, self.server_port), self.credentials)
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)

        self.streamChannelRequest = p4runtime_pb2.StreamMessageRequest()
        self.sendRequest = True

    def StreamChannel(self):
        global dev_id

        # Prepare an authentication request.
        login = auth_pb2.Auth()
        login.user_name = "admin"
        login.passwd = "admin"
        self.streamChannelRequest.other.Pack(login)

        def request():
            while True:
                if self.sendRequest:
                    self.sendRequest = False
                    yield self.streamChannelRequest
                else:
                    yield p4runtime_pb2.StreamMessageRequest()

        return self.stub.StreamChannel(request())

    def WriteTableEntry(self, update_type, table, match_key, action_data):
        global dev_id
        request = p4runtime_pb2.WriteRequest()
        request.device_id = dev_id
        request.election_id.low = 1

        update = request.updates.add()
        update.type = update_type
        update.entity.table_entry.table_id = table
        update.entity.table_entry.is_default_action = 1
        update.entity.table_entry.action.action.action_id = 1

        matches = update.entity.table_entry.match.add()
        matches.field_id = 1
        matches.exact.value = bytes(match_key)

        act = update.entity.table_entry.action.action.params.add()
        act.param_id = 2
        act.value = bytes(action_data)

        ServerConfig.print_debug("Sending table write request to server:")
        ServerConfig.print_debug(request)
        try:
            self.stub.Write(request)
        except grpc.RpcError as error:
            ServerConfig.print_debug("An error ocurred during a 'write' execution!")
            ServerConfig.print_debug("{}: {}".format(error.code().name, error.details()))

        return

    def ReadTableEntry(self, table, match_key):
        global dev_id
        request = p4runtime_pb2.ReadRequest()
        request.device_id = dev_id

        entity = request.entities.add()
        entity.table_entry.table_id = table
        matches = entity.table_entry.match.add()
        matches.field_id = 1
        matches.exact.value = bytes(match_key)

        ServerConfig.print_debug("Sending table read request to server:")
        ServerConfig.print_debug(request)
        try:
            for response in self.stub.Read(request):
                ServerConfig.print_debug("Table read response received from server:")
                ServerConfig.print_debug(response)
        except grpc.RpcError as error:
            ServerConfig.print_debug("An error occured during a 'read' execution!")
            ServerConfig.print_debug("{}: {}\n".format(error.code().name, error.details()))

        return

def main():

    devicesWrite = [False, False, False]

    client = P4RuntimeClient()

    streamC = client.StreamChannel()

    sleep(0.5)

    tables_initialized = False
    while True:
        try:
            packet = next(streamC)

            if packet.HasField("packet"):
                # Print packet information.
                ServerConfig.print_debug("Received packet:")
                ServerConfig.print_debug("Payload: {}".format(hexlify(packet.packet.payload)))
                ServerConfig.print_debug("Switch id: {}".format(packet.packet.metadata[0].metadata_id))
                ServerConfig.print_debug("Input port: {}\n".format(hexlify(packet.packet.metadata[0].value)))

                # Extract packet.
                pkt = Ether(_pkt=packet.packet.payload)
                eth_src = pkt.getlayer(Ether).src
                eth_dst = pkt.getlayer(Ether).dst
                ether_type = pkt.getlayer(Ether).type
                ServerConfig.print_debug("Received Ethernet frame {} => {} type_hex {}".format(eth_src, eth_dst, hex(ether_type)))

		# The packet can be either ipv4 or 802.1q (vlan).
                if (ether_type == 2048 or ether_type == 33024) and not devicesWrite[packet.packet.metadata[0].metadata_id - 1]:
                    devicesWrite[packet.packet.metadata[0].metadata_id - 1] = True

    	            # Print packet data.
            	    ip_src = pkt[IP].src
                    ip_dst = pkt[IP].dst
                    ServerConfig.print_debug("Ethernet frame has IPv4 packet {} => {}".format(ip_src, ip_dst))

            if packet.HasField("other"):
                if packet.other.value == "\n\014Auth success":

                    ServerConfig.print_debug("Received authentication response from server:")
                    ServerConfig.print_debug(packet)

                    # Prepare an arbitration request.
                    client.streamChannelRequest = p4runtime_pb2.StreamMessageRequest()
                    client.streamChannelRequest.arbitration.device_id = 1
                    client.streamChannelRequest.arbitration.role.id = 1
                    client.sendRequest = True

            if packet.HasField("arbitration"):
                ServerConfig.print_debug("Received arbitration response from server:")
                ServerConfig.print_debug(packet)

        except IndexError:
            continue

if __name__ == "__main__":
    main()
