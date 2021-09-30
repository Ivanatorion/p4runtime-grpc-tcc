#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
import socket
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

SWITCH_TO_HOST_PORT = 1
SWITCH_TO_SWITCH_PORT = 2



def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

  

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        #s1.MasterArbitrationUpdateComplete()
        #s2.MasterArbitrationUpdateComplete()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s1"
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s2"

        table_entry = p4info_helper.buildTableEntry(
        	table_name="MyIngress.ipv4_lpm",
        	match_fields={
            	"hdr.ipv4.dstAddr": ("10.0.2.22", 32)
        	},
        	action_name="MyIngress.ipv4_forward",
        	action_params={
            	"dstAddr": "08:00:00:00:02:22",
            	"port": 4
        	}
        )

        s2.WriteTableEntry(table_entry)

        #f = open("/home/guilherme/Documents/p4runtime-grpc-v3/write_request_file.txt")
        #write_request = f.read()

        #if write_request is not None:
       # 	s2.WriteTableEntry(table_entry)
        	#print s2.WriteTableEntry(table_entry)
        	#print write_request
                #s2.WriteFlowRule(write_request)
	#	print "Flow rule installed in the switch"

        # Write the rules that tunnel traffic from h1 to h2
        #writeTunnelRules(p4info_helper, ingress_sw=s1, egress_sw=s2, tunnel_id=100,
                        # dst_eth_addr="08:00:00:00:02:22", dst_ip_addr="10.0.2.2")

        # Write the rules that tunnel traffic from h2 to h1
        #writeTunnelRules(p4info_helper, ingress_sw=s2, egress_sw=s1, tunnel_id=200,
                        # dst_eth_addr="08:00:00:00:01:11", dst_ip_addr="10.0.1.1")

        # TODO Uncomment the following two lines to read table entries from s1 and s2
        # readTableRules(p4info_helper, s1)
        # readTableRules(p4info_helper, s2)

        # Print the tunnel counters every 2 seconds
      
    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
