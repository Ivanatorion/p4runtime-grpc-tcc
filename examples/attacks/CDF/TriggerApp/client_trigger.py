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
        login.user_name = "ivan1"
        login.passwd = "ivan1"
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

def toHex(n):
    values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]

    if n <= 0 or n > 255:
        return "00"

    return values[n/16] + values[n%16]

def main():
    global dev_id

    client = P4RuntimeClient()

    streamC = client.StreamChannel()

    switch_count = 50

    for i in range(0, switch_count):
        dst_addr = "0800000001%s" % (toHex(i+3))

        while(client.sendRequest):
            sleep(0.000001)

        # Packet out.
        client.streamChannelRequest = p4runtime_pb2.StreamMessageRequest()
        client.streamChannelRequest.packet.payload = (dst_addr + "08000000010181000001000008004A000032000100003C1162B80A0001010A0002021F24000200000002000000000000000100000FA004D210E1000A82F07034").decode("hex")
        metadata = client.streamChannelRequest.packet.metadata.add()
        metadata.metadata_id = 1
        metadata.value = struct.pack("B", 1)
        client.sendRequest = True
        print "Packet-out: %s" % dst_addr

    sleep(10)

if __name__ == "__main__":
    main()
