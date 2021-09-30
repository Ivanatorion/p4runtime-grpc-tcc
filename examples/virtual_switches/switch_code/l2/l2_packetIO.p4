// Copyright (c) 2019 Mateus Saquetti
// All rights reserved.
//
// This software is a fork from P4-NetFPGA project and was developed by
// Institute of Informatics of the Federal University of Rio Grande do Sul
// (INF-UFRGS)
//
// @NETFPGA_LICENSE_HEADER_START@
//
// Licensed to NetFPGA C.I.C. (NetFPGA) under one or more contributor
// license agreements.  See the NOTICE file distributed with this work for
// additional information regarding copyright ownership.  NetFPGA licenses this
// file to you under the NetFPGA Hardware-Software License, Version 1.0 (the
// "License"); you may not use this file except in compliance with the
// License.  You may obtain a copy of the License at:
//
//   http://www.netfpga-cic.org
//
// Unless required by applicable law or agreed to in writing, Work distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations under the License.
//
// @NETFPGA_LICENSE_HEADER_END@
//
// Description:
//     Simple l2-layer switch example to packet in/out
//

#include <core.p4>
#include <sume_switch.p4>

typedef bit<48> EthAddr_t;
typedef bit<32> IPv4Addr_t;

#define VLAN_TYPE 0x8100
#define IPV4_TYPE 0x0800

// standard Ethernet header
header Ethernet_h {
    EthAddr_t dstAddr;
    EthAddr_t srcAddr;
    bit<16> etherType;
}

// standard Vlan header
header Vlan_h {
    bit<3> prio;
    bit<1> dropEligible;
    bit<12> vlanId;
    bit<16> etherType;
}

// List of all recognized headers
struct Parsed_packet {
    Ethernet_h ethernet;
    Vlan_h vlan;
}

// user defined metadata: can be used to shared information between
// TopParser, TopPipe, and TopDeparser
struct user_metadata_t {
    bit<8>  unused;
}

// digest data to be sent to CPU if desired. MUST be 256 bits!
struct digest_data_t {
    bit<256>  unused;
}

// Parser Implementation
@Xilinx_MaxPacketRegion(16384)
parser TopParser(packet_in pkt_in,
                 out Parsed_packet hdr,
                 out user_metadata_t user_metadata,
                 out digest_data_t digest_data,
                 inout sume_metadata_t sume_metadata) {
    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt_in.extract(hdr.ethernet);
        user_metadata.unused = 0;
        digest_data.unused = 0;
        transition select(hdr.ethernet.etherType) {
            VLAN_TYPE: parse_vlan;
            default: reject;
        }
    }

    state parse_vlan {
        pkt_in.extract(hdr.vlan);
        transition accept;
    }
}

// match-action pipeline
control TopPipe(inout Parsed_packet hdr,
                inout user_metadata_t user_metadata,
                inout digest_data_t digest_data,
                inout sume_metadata_t sume_metadata) {

    action forward(bit<8> port) {
        sume_metadata.dst_port = port;
    }
    table dmac {
        actions = {
            forward;
        }
        key = {
            hdr.ethernet.dstAddr: exact;
        }
        size = 64;
    }

    action send_to_control() {
        // Doing packet in. Sending the packet to control through nf3_dma
        sume_metadata.dst_port = 8w0b10000000; // nf3
    }

    apply {
        // check if dst Ethernet address is in the forwarding database
        if (!dmac.apply().hit) {
            // unknown destination MAC address
            send_to_control();
        }
    }


}

// Deparser Implementation
@Xilinx_MaxPacketRegion(16384)
control TopDeparser(packet_out pkt_out,
                    in Parsed_packet hdr,
                    in user_metadata_t user_metadata,
                    inout digest_data_t digest_data,
                    inout sume_metadata_t sume_metadata) {
    apply {
        pkt_out.emit(hdr.ethernet);
        pkt_out.emit(hdr.vlan);
    }
}

// Instantiate the switch
SimpleSumeSwitch( TopParser(), TopPipe(), TopDeparser() ) main;
