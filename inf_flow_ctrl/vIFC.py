from events import EventType
from InfoGraph import InfoGraph
from utils.Auth import *
from utils.SwitchConf import *
from server.connections import *
from server.connections.ConnectionArray import *

from inf_flow_ctrl.Hash import *
from inf_flow_ctrl.events import PacketEvent
from inf_flow_ctrl.events import FlowruleEvent

from config import ServerConfig

import time

from scapy.all import *

info_graph = InfoGraph()

class VerifyEvent():

    @staticmethod
    def init_vifc():
        if ServerConfig.VIFC:
            for switch_name in SwitchConf.getAllSwitchNames():
                VerifyEvent.add_switch(switch_name[0])
            for user_name in Auth.getAllUserNames():
                VerifyEvent.add_user(user_name[0], Auth.getUserLabels(user_name[0]))

            policies = Auth.getPolicies()
            info_graph.setPolicies(policies)

    # Add a switch node to the graph.
    @staticmethod
    def add_switch(switch_name):
        info_graph.add_node(switch_name, False, [])
        return

    # Add an user (application) to the graph.
    @staticmethod
    def add_user(user, labels):
        info_graph.add_node(user, True, labels)
        return

    # Check for flow violations during events.
    @staticmethod
    def verify_event_packet_in(packet, context):
        if not ServerConfig.VIFC:
            return (VIFC_RESPONSE_NONE, 0)

        pkt = Ether(_pkt=packet.payload)

        eth_src = pkt.getlayer(Ether).src
        eth_dst = pkt.getlayer(Ether).dst
        ether_type = pkt.getlayer(Ether).type

        ips = ""
        ipd = ""

        if ether_type == 2048:
            ips = pkt[IP].src
            ipd = pkt[IP].dst
        elif ether_type == 2054:
            ips = pkt[ARP].psrc
            ipd = pkt[ARP].pdst

        infoP = (str(ips) + str(ipd) + str(eth_src) + str(eth_dst))

        return_value = (VIFC_RESPONSE_NONE, 0)

        start_time = time.time()
        switch_name = SwitchConf.getSwitchById(packet.metadata[0].metadata_id).switch_name
        end_time = time.time()
        #print "PROFILING (getSwitchById):             %.9f" % (end_time - start_time)

        start_time = time.time()
        user_name = ConnectionArray.getUsername(context.peer())
        if "_" in user_name:
            split_user = user_name.split("_")
            user_name = split_user[1]
        end_time = time.time()
        #print "PROFILING (getUsername):               %.9f" % (end_time - start_time)

        start_time = time.time()
        pkt_hash = Hash.packet_to_hash(infoP)
        end_time = time.time()
        #print "PROFILING (packet_to_hash):            %.9f" % (end_time - start_time)

        start_time = time.time()
        event = PacketEvent.PacketEvent(switch_name, user_name, pkt_hash)
        end_time = time.time()
        #print "PROFILING (PacketEvent - constructor): %.9f" % (end_time - start_time)

        # Add an event.
        if event.type == EventType.PACKET_EVENT:
            start_time = time.time()
            return_value = info_graph.add_event(event)
            end_time = time.time()
        #print "PROFILING (add_event):                 %.9f" % (end_time - start_time)

        # For debug purposes.
        #info_graph.print_nodes()
        #info_graph.print_edges()

        return return_value

    @staticmethod
    def verify_event_packet_out(packet, context):
        if not ServerConfig.VIFC:
            return (VIFC_RESPONSE_NONE, 0)

        pkt = Ether(_pkt=packet.payload)

        eth_src = pkt.getlayer(Ether).src
        eth_dst = pkt.getlayer(Ether).dst
        ether_type = pkt.getlayer(Ether).type

        ips = ""
        ipd = ""

        if ether_type == 2048:
            ips = pkt[IP].src
            ipd = pkt[IP].dst
        elif ether_type == 2054:
            ips = pkt[ARP].psrc
            ipd = pkt[ARP].pdst

        infoP = (str(ips) + str(ipd) + str(eth_src) + str(eth_dst))

        return_value = (VIFC_RESPONSE_NONE, 0)

        start_time = time.time()
        switch_name = SwitchConf.getSwitchById(packet.metadata[0].metadata_id).switch_name
        end_time = time.time()
        #print "PROFILING (getSwitchById):             %.9f" % (end_time - start_time)

        start_time = time.time()
        user_name = ConnectionArray.getUsername(context.peer())
        end_time = time.time()
        #print "PROFILING (getUsername):               %.9f" % (end_time - start_time)

        start_time = time.time()
        pkt_hash = Hash.packet_to_hash(infoP)
        end_time = time.time()
        #print "PROFILING (packet_to_hash):            %.9f" % (end_time - start_time)

        start_time = time.time()
        event = PacketEvent.PacketEvent(user_name, switch_name, pkt_hash)
        end_time = time.time()
        #print "PROFILING (PacketEvent - constructor): %.9f" % (end_time - start_time)

        # Add an event.
        if event.type == EventType.PACKET_EVENT:
            start_time = time.time()
            return_value = info_graph.add_event(event)
            end_time = time.time()
            #print "PROFILING (add_event):                 %.9f" % (end_time - start_time)

        # For debug purposes.
        #info_graph.print_nodes()
        #info_graph.print_edges()

        return return_value
