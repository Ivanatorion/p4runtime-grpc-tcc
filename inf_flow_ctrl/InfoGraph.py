from events import EventType
from events.PacketEvent import PacketEvent
from InfoNode import InfoNode
from config import PermEnum

MAX_PACKETS = 80

class InfoGraph():

    def __init__(self):
        self.nodes = []
        self.edges = set()

        self.packet_events = {} #Stores packet labels
        self.policies = []

        self.packet_hash_list = [None] * MAX_PACKETS
        self.packet_hash_list_pointer = 0

    def setPolicies(self, policies):
        self.policies = policies

    @staticmethod
    def higher_rank(higher, lower):
        for label in lower:
            if label not in higher:
                return False
        return True

    def get_pol_response(self, src, dst):
        dst_tags = set()
        src_tags = set()
        dst_switches = set()

        for lab in dst:
            dst_tags.add(lab[0])
            dst_switches.add(lab[1])

        for tag in dst_tags:
            has_tag = True
            for sw in dst_switches:
                if (tag, sw) not in src:
                    has_tag = False
            if has_tag:
                src_tags.add(tag)

        for pol in self.policies:
            pol_source_applies = True

            nTags = set()
            gTags = set()

            if pol[0] & PermEnum.VIFC_DEVICE != 0:
                nTags.add(PermEnum.VIFC_DEVICE)
            if pol[0] & PermEnum.VIFC_FLOWRULE != 0:
                nTags.add(PermEnum.VIFC_FLOWRULE)
            if pol[0] & PermEnum.VIFC_PACKET != 0:
                nTags.add(PermEnum.VIFC_PACKET)
            if pol[0] & PermEnum.VIFC_CONFIG != 0:
                nTags.add(PermEnum.VIFC_CONFIG)

            if pol[1] & PermEnum.VIFC_DEVICE != 0:
                gTags.add(PermEnum.VIFC_DEVICE)
            if pol[1] & PermEnum.VIFC_FLOWRULE != 0:
                gTags.add(PermEnum.VIFC_FLOWRULE)
            if pol[1] & PermEnum.VIFC_PACKET != 0:
                gTags.add(PermEnum.VIFC_PACKET)
            if pol[1] & PermEnum.VIFC_CONFIG != 0:
                gTags.add(PermEnum.VIFC_CONFIG)

            for p_needed in nTags:
                if p_needed not in src_tags:
                    pol_source_applies = False
            if pol_source_applies:
                pol_dst_applies = True
                for p_granted in gTags:
                    if p_granted not in dst_tags:
                        pol_dst_applies = False
                if pol_dst_applies:
                    return (pol[2], pol[3]) #Response, Message

        return (PermEnum.VIFC_RESPONSE_BLOCK, 0)

    @staticmethod
    def intersect_labels(labels1, labels2):
        if len(labels1) == 0:
            return labels2
        if len(labels2) == 0:
            return labels1

        new_labels = set()
        for label in labels1:
            if label in labels2:
                new_labels.add(label)
        return new_labels

    def add_node(self, node_name, is_app, labels):
        for node in self.nodes:
            if node.name == node_name:
                return False

        new_node = InfoNode(node_name, is_app, labels)
        self.nodes.append(new_node)
        return True

    def __add_edge(self, src_node_name, dst_node_name):
        edge = (src_node_name, dst_node_name)
        self.edges.add(edge)
        return True

    def add_event(self, event):
        return_value = (PermEnum.VIFC_RESPONSE_NONE, 0)

        src_node = False
        dst_node = False
        for node in self.nodes:
            if node.name == event.src:
                src_node = node
            if node.name == event.dst:
                dst_node = node

        if src_node == False or dst_node == False:
            return (PermEnum.VIFC_RESPONSE_BLOCK, 0)

        if event.type == EventType.PACKET_EVENT:
            try: #Check if this packet was seen before
                event.labels = self.packet_events[event.pktout]
                if src_node.is_app:
                    event.labels = InfoGraph.intersect_labels(event.labels, src_node.labels)
            except KeyError: #New Packet
                if len(event.labels) == 0 and src_node.is_app:
                    event.labels = src_node.labels

                if self.packet_hash_list[self.packet_hash_list_pointer] != None:
                    self.packet_events.pop(self.packet_hash_list[self.packet_hash_list_pointer])

                self.packet_hash_list[self.packet_hash_list_pointer] = event.pktout
                self.packet_hash_list_pointer = (self.packet_hash_list_pointer + 1) % MAX_PACKETS

            self.packet_events[event.pktout] = event.labels


            self.__add_edge(src_node.name, dst_node.name)

            if len(event.labels) > 0 and dst_node.is_app and not InfoGraph.higher_rank(event.labels, dst_node.labels):
                return_value = self.get_pol_response(event.labels, dst_node.labels)

        return return_value

    # -------- Debug Methods -------- #
    def print_nodes(self):
        print "\nGraph nodes:"
        for node in self.nodes:
            print "{}".format(node.name)
        return

    def print_edges(self):
        print "\nGraph edges:"
        for edge in self.edges:
            print edge
        return
