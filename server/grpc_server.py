from concurrent import futures
import grpc
import json, os, re, ast
import unicodedata
import sys
import socket
import thread
import time
import signal

from p4.v1 import p4runtime_pb2 as p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc as p4runtime_pb2_grpc

from protobuffs.code_pb2 import *
from protobuffs.auth_pb2 import *

from utils.RPC_mgmt import *
from server.connections import *
from sniffer import Sniffer
from config import ServerConfig
from utils import ServerLog
from examples.virtual_switches.LoadVSwitch import *
from utils.Auth import *
from utils.SwitchConf import *
from server.connections.ConnectionArray import *

from inf_flow_ctrl.vIFC import *

class PacketInStruct():
    def __init__(self):
        self.packetInResponse = p4runtime_pb2.StreamMessageResponse()
        self.packetInResponse.packet.payload = " "
        self.metadata = self.packetInResponse.packet.metadata.add()
        self.metadata.metadata_id = 0
        self.metadata.value = " "

        self.packet_id = 0

class P4Runtime(p4runtime_pb2_grpc.P4RuntimeServicer):

    def __init__(self):
        self.host = ServerConfig.HOST
        self.server_port = ServerConfig.SERVER_PORT
        self.device_id = 0

        with open(ServerConfig.SERVER_CERTIFICATE, "rb") as file:
            trusted_certs = file.read()

        self.credentials = grpc.ssl_channel_credentials(root_certificates=trusted_certs)
        self.channel = grpc.secure_channel("{}:{}".format(self.host, self.server_port), self.credentials)
        self.stub = p4runtime_pb2_grpc.P4RuntimeStub(self.channel)

    def SetForwardingPipelineConfig(self, request, context):
        return RPC_mgmt.process_setPipe(request, context)

    def GetForwardingPipelineConfig(self, request, context):
        return RPC_mgmt.process_getPipe(request, context)

    def StreamChannel(self, request_iterator, context):
        return RPC_mgmt.process_streamChannel(self, request_iterator, context)

    def Write(self, request, context):
        return RPC_mgmt.process_write_request(self, request, context)

    def Read(self, request, context):
        return RPC_mgmt.process_read_request(request, context)

packetLim = [False] * 101

def sniffer_thread():
    global packetLim

    sniffer_instance = Sniffer(ServerConfig.PACKETIN_IFACE, 1500)

    newPacketIn = PacketInStruct()
    c_packet_id = 0

    print "Sniffer Thread Started"

    while True:
        pack_data = sniffer_instance.recv_packet_in()
        if (pack_data != False) and pack_data[0] >= 0 and pack_data[0] < len(packetLim) and (not packetLim[pack_data[0]]):
            packetLim[pack_data[0]] = True

            newPacketIn = PacketInStruct()
            newPacketIn.packetInResponse = p4runtime_pb2.StreamMessageResponse()
            newPacketIn.packetInResponse.packet.payload = pack_data[2]
            newPacketIn.metadata = newPacketIn.packetInResponse.packet.metadata.add()
            newPacketIn.metadata.metadata_id = pack_data[0]
            newPacketIn.metadata.value = pack_data[1]
            newPacketIn.packet_id = c_packet_id

            c_packet_id = c_packet_id + 1

            print "EXPT: Packet-in (%d): interface => server %.9f" % (c_packet_id, time.time())
            ConnectionArray.sendPacketInToBuffer(newPacketIn)

def packet_limit_thread():
    global packetLim

    print "PacketLim Thread Started"

    while True:
        for i in range(0, len(packetLim)):
            packetLim[i] = False
        sleep(1.1)

def close_sig(*args):
    ServerLog.close_log()
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, close_sig)

    LOG_F = ServerLog.open_log('logs/pvs_log')

    LoadVSwitch.load_switches()

    Auth.loadDbMemory()
    SwitchConf.loadDbMemory()

    #Plugins
    VerifyEvent.init_vifc()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p4runtime_instance = P4Runtime()
    p4runtime_pb2_grpc.add_P4RuntimeServicer_to_server(p4runtime_instance, server)

    with open(ServerConfig.SERVER_KEY, "rb") as file:
        private_key = file.read()
    with open(ServerConfig.SERVER_CERTIFICATE, "rb") as file:
        certificate_chain = file.read()

    server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain,),))
    # server.add_insecure_port('localhost:50052')
    server.add_secure_port("[::]:{}".format(p4runtime_instance.server_port), server_credentials)
    server.start()
    print "PvS P4Runtime server running @ grpcs://{}:{}".format(p4runtime_instance.host, p4runtime_instance.server_port)

    thread.start_new_thread(sniffer_thread, ())
    thread.start_new_thread(packet_limit_thread, ())

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        ServerLog.close_log()
