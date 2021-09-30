from binascii import *
import struct
import socket
import datetime

import grpc

import json, os, re, ast, sys

from platform_api import p4_regs_api as p4_regs_api
from platform_api import p4_tables_api as p4_tables_api
from platform_api import p4_px_tables as p4_px_tables

from p4.v1 import p4runtime_pb2 as p4runtime_pb2
from p4.v1 import p4runtime_pb2_grpc as p4runtime_pb2_grpc

from protobuffs import auth_pb2 as auth_pb2
from protobuffs import code_pb2 as code_pb2

from SwitchConf import *
from Auth import *
from model.DB_mgmt import *

from server.connections import *
from server.connections.ConnectionArray import *

from config import PermEnum
from config import SwitchTypeEnum
from config import ServerConfig

from utils import convert
from utils import ServerLog
from utils.bmv2 import BMV2_connection

from time import sleep
import time

from inf_flow_ctrl.events import PacketEvent
from inf_flow_ctrl.events import FlowruleEvent
from inf_flow_ctrl.vIFC import *

PACKETOUT_SOCKET = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
PACKETOUT_SOCKET.bind((ServerConfig.PACKETOUT_IFACE, 0))

class RPC_mgmt():

    @staticmethod
    def MasterArbitration(self, request, context):
        resp = p4runtime_pb2.StreamMessageResponse()
        request.arbitration.device_id = 1
        resp.arbitration.CopyFrom(request.arbitration)
        resp.arbitration.status.code = code_pb2.OK
        return resp

    @staticmethod
    def process_streamChannel(self, request_iterator, context):
        peer_key = context.peer()
        userAuthenticated = False
        login = False

        while True:
            try:
                req = next(request_iterator)
            except grpc.RpcError as e: # End of connection
                if login is not False:
                    ConnectionArray.remove(peer_key)
                return

            if userAuthenticated:
                packet_in = ConnectionArray.getPacketInFromBuffer(login.user_name)
                if packet_in is not False:
                    # -------- Begin Info Flow Control -------- #
                    print "EXPT: vIFC Start %.9f" % time.time()
                    ifc_result = VerifyEvent.verify_event_packet_in(packet_in.packetInResponse.packet, context)
                    print "EXPT: vIFC Finish %.9f" % time.time()

                    if ifc_result[0] == VIFC_RESPONSE_BLOCK:
                        print "IFC Blocked Flow"
                        context.set_code(grpc.StatusCode.CANCELLED)
                        context.set_details("Attempted CAP Attack block by vIFC")
                        ServerLog.print_log("IFC Blocked flow of Packet-in (%d) was being sent to (%s): %.9f" % (packet_in.packet_id, login.user_name, time.time()))
                    else:
                        if ifc_result[0] == VIFC_RESPONSE_WARN:
                            print "IFC Warned Flow: {}".format(ifc_result[1])
                            ServerLog.print_log("IFC Warned flow of Packet-in (%d) sent to (%s): %.9f" % (packet_in.packet_id, login.user_name, time.time()))

                        print "EXPT: Packet-in (%d): server => controller: %.9f" % (packet_in.packet_id, time.time())
                        print packet_in.packetInResponse
                        yield packet_in.packetInResponse
                        ServerLog.print_log("Packet-in (%d) sent to (%s): %.9f" % (packet_in.packet_id, login.user_name, time.time()))
                    # --------- End Info Flow Control --------- #

            # Authentication message.
            if req.HasField("other") and req.other.type_url == "type.googleapis.com/Auth":
                ServerConfig.print_debug("Received authentication message from {}({}):".format(
                         context.peer(), ConnectionArray.getUsername(context.peer())))
                ServerConfig.print_debug(req)

                # Add the connection to the pool.
                login = auth_pb2.Auth.FromString(req.other.value)
                ConnectionArray.add(peer_key, login.user_name)
                username = ConnectionArray.getUsername(context.peer())

                # Authenticate the current connection if it isn't authenticated yet.
                # Keep in mind that an user with the CONNECTED state is not authenticated.
                if ConnectionArray.isConnected(context.peer()) is True:
                    if Auth.authenticate(login.user_name, login.passwd) is True:
                        userAuthenticated = True
                        ConnectionArray.authenticate(context.peer())
                    else:
                        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                        context.set_details("Invalid username or password")
                        yield p4runtime_pb2.StreamMessageResponse()

                succ = auth_pb2.Auth()
                succ.user_name = "Auth success"
                succ.passwd = ""
                resp = p4runtime_pb2.StreamMessageResponse()
                resp.other.Pack(succ)
                yield resp

            # Arbitration update.
            elif req.HasField("arbitration"):
                ServerConfig.print_debug("Received master arbitration message from peer '{}' ({}):".format(
                         context.peer(), ConnectionArray.getUsername(context.peer())))
                ServerConfig.print_debug(req)
                yield RPC_mgmt.MasterArbitration(self, req, context)

            # Packet-out message.
            elif req.HasField("packet"):
                packet = req.packet
                print "EXPT: Packet-out: controller => server %.9f" % time.time()

                ServerConfig.print_debug("Packet-out arrived from the controller, for switch {} input port {}".format(
                          packet.metadata[0].metadata_id,hexlify(packet.metadata[0].value)))

                # -------- Begin Info Flow Control -------- #
                print "EXPT: vIFC Start %.9f" % time.time()
                ifc_result = VerifyEvent.verify_event_packet_out(packet, context)
                print "EXPT: vIFC Finish %.9f" % time.time()
                if ifc_result[0] == VIFC_RESPONSE_BLOCK:
                    print "IFC Blocked Flow"
                elif ifc_result[0] == VIFC_RESPONSE_WARN:
                    print "IFC Warned Flow: {}".format(ifc_result[1])
                # --------- End Info Flow Control --------- #

                # print "Payload: {}".format(hexlify(packet.payload)) # we need to be quick
                RPC_mgmt.ProcessPacketOut(packet)
                print "EXPT: Packet-out: server => interface %.9f" % time.time()
                ServerLog.print_log("Packet-out from (%s) to switch (%d): %.9f" % (login.user_name, int(packet.metadata[0].metadata_id), time.time()))

    @staticmethod
    def ProcessPacketOut(packet_out):
        # Retrieving values from the packet.
        metadata = packet_out.metadata[0]
        switch_id = int(metadata.metadata_id)
        input_port = metadata.value
        payload = packet_out.payload

        # Calling the method to send the packet to the network interface.
        #print(packet_out)
        RPC_mgmt.SendPacket(switch_id, input_port, payload)

    @staticmethod
    def SendPacket(switch_id, switch_port, payload):
        switch = SwitchConf.getSwitchById(switch_id)
        if(switch.switch_type == SwitchTypeEnum.TYPE_BMV2):
            return PACKETOUT_SOCKET.send(payload + struct.pack("B", switch_id) + switch_port)
        else:
            return PACKETOUT_SOCKET.send(struct.pack("B", switch_id) + switch_port + payload)

    @staticmethod
    def process_getPipe(request, context):
        config = p4runtime_pb2.ForwardingPipelineConfig()
        try:
            config.cookie.CopyFrom(p4_cookie)
        except:
            print "Method process_getPipe called, however p4_cookie still not defined"
        return p4runtime_pb2.GetForwardingPipelineConfigResponse(config = config)

    @staticmethod
    def process_setPipe(request, context):
        ServerConfig.print_debug("Method process_setPipe called from client...")
        switch_id = request.device_id
        switch = SwitchConf.getSwitchById(switch_id)
        if switch is False:
            ServerConfig.print_debug("Switch with id {} not found".format(switch_id))
            return code_pb2.NOT_FOUND

        global p4_cookie
        response = request
        p4_cookie = response.config.cookie
        response.device_id = request.device_id
        response.role_id = request.role_id
        p4info = None
        p4_device_config = None
        config = p4runtime_pb2.ForwardingPipelineConfig()
        if p4info:
            config.p4info.CopyFrom(p4info)
        if p4_device_config:
            config.p4_device_config = p4_device_config.SerializeToString()
        response.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
        return p4runtime_pb2.SetForwardingPipelineConfigResponse()

    @staticmethod
    def process_write_request(self, request, context):
        peer_key = context.peer()
        username = ConnectionArray.getUsername(peer_key)
        ServerConfig.print_debug("Received write request from peer {}({}):".format(peer_key, username))

        ServerLog.print_log("Received write request (%s): %.9f" % (username, time.time()))

        response = request

        # Verify if the user is authenticated.
        if ConnectionArray.isAuthenticated(peer_key) is False:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("User {} is not authenticated".format(username))
            return response

        # Get the switch object from memory.
        switch = SwitchConf.getSwitchById(request.device_id)
        if switch == False:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Switch with id {} not found".format(switch_id))
            return response

        # Verify permissions
        for request_update in request.updates:
            if request_update.entity.HasField("table_entry"):
                # Verify if the user has permission to write table entries into the requested switch.
                if ConnectionArray.verifyPermission(context, switch, PermEnum.DEVICE_WRITE | PermEnum.FLOWRULE_WRITE) is False:
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User {} does not have permission to write table entries into switch {}".format(username, switch.switch_name))
                    return response

        if switch.switch_type == SwitchTypeEnum.TYPE_BMV2:
            response = RPC_mgmt.process_write_request_bmv2(request)
        elif switch.switch_type == SwitchTypeEnum.TYPE_PVS:
            response = RPC_mgmt.process_write_request_pvs(request)

        ServerLog.print_log("Write Request success (%s): %.9f" % (username, time.time()))
        return response

    @staticmethod
    def process_write_request_bmv2(request):
        return BMV2_connection.process_write_bmv2(request)

    @staticmethod
    def process_write_request_pvs(request):
        switch = SwitchConf.getSwitchById(request.device_id)

        for request_update in request.updates:
            if request_update.entity.HasField("table_entry"):

                switch_id = switch.switch_id
                table_id = request_update.entity.table_entry.table_id

                switch_table = SwitchConf.getSwitchTableById(switch.switch_id, table_id)
                if switch_table == False:
                    ontext.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Table with id {} from switch {} not found".format(table_id, switch.switch_name))
                    return response

                action_id = request_update.entity.table_entry.action.action.action_id

                try:
                    table_action = SwitchConf.table_action_dict[switch_id, table_id, action_id]
                except KeyError:
                    context.set_code(grpc.StatusCode.NOT_FOUND)
                    context.set_details("Action with id {} from table {}, switch {} not found".format(action_id, switch_table.table_name, switch.switch_name))
                    return response

                # Necessary match manipulations.
                match = request_update.entity.table_entry.match[0]
                match_key = request_update.entity.table_entry.match[0].exact.value
                match_key = match_key.split()

		        # Necessary action manipulations
                action_params = request_update.entity.table_entry.action.action.params
                action_key = action_params[0].value
                action_key = action_key.split()

                check_bytestr = re.match("[\\x00-\\x1F\\x80-\\xFF]", match_key[0])
                if check_bytestr:
                    # Match value contains a byte string
                    # Need to decode it
                    match_hexvalue = hexlify(match_key[0])
                    action_hexvalue = hexlify(action_key[0])
                    if convert.matchesMac(match_hexvalue) == True:
                        decoded_key = convert.decodeMac(match_key[0])
                        match_key = []
                        match_key.insert(0, decoded_key)
                    if convert.matchesPort(action_hexvalue) == True:
                        decoded_port = convert.decodePort(action_hexvalue)
                        action_key = []
                        action_key.insert(0, decoded_port)
                    if convert.matchesIPv4(match_key) == True:
                        decoded_key = convert.decodeIpv4(match_key[0])
                        match_key = []
                        match_key.insert(0, decoded_key)
                else:
                    #match contains a normal string
                    match_key = ast.literal_eval(json.dumps(match_key))
                    action_key = ast.literal_eval(json.dumps(action_key))

                # Insert an entry.
                if request_update.type == p4runtime_pb2.Update.INSERT:
                    if match.HasField("exact"):
                        p4_tables_api.table_cam_add_entry(switch, switch_table, table_action, match_key, action_key)

                # Update an entry.
                elif request_update.type == p4runtime_pb2.Update.MODIFY:
                    # First: Read the entry provided by the client to see its existance in the switch.
                    # TODO: hardcoded yet, need to remove dependence on switch specific p4_tables_api.
                    if match.HasField("exact"):
                        # key = map(p4_px_tables.convert_to_int, match_key)
                        (found, val) = p4_tables_api.table_cam_read_entry(switch_table.switch_id, switch_table.table_name, match_key)
                        if found != "False":
                            # p4_tables_api.table_cam_delete_entry(switch_table.switch_id, switch_table.table_name, match_key)
                            # Second: Modify the existing entry with the values stored in the variables.
                            ServerConfig.print_debug("Match key: {} exists in table {} of switch {}: found {}, val {}. Updating...".
                                    format(match_key, switch_table.table_name, switch.switch_name, found, val))
                            p4_tables_api.table_cam_add_entry(switch_table.switch_id, switch_table.table_name, match_key, action_name, action_key)
                        else:
                            ServerConfig.print_debug("Error: Match key {} not found in table {} of switch {}".
                                   format(match_key, switch_table.table_name, switch.switch_name))
                            response = p4runtime_pb2.Error()
                            response.canonical_code = code_pb2.NOT_FOUND
                            return response

                # Delete an entry.
                elif request_update.type == p4runtime_pb2.Update.DELETE:

                    # First: Use read entry which will check the existence, then delete it.
                    if match.HasField("exact"):
                        # key = map(p4_px_tables.convert_to_int, match_key)
                        (found, val) = p4_tables_api.table_cam_read_entry(switch_table.switch_id, switch_table.table_name, match_key)
                        if found != "False":
                            ServerConfig.print_debug("Match key: {} exists in table {} of switch {}: found {}, val {}. Deleting...".
                                    format(match_key, switch_table.table_name, switch.switch_name, found, val))
                            p4_tables_api.table_cam_delete_entry(switch_table.switch_id, switch_table.table_name, match_key)
                        else:
                            ServerConfig.print_debug("Error: Match key {} not found in table {} of switch {}".
                                    format(match_key, switch_table.table_name, switch.switch_name))

                else:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Update code {} is invalid. Please inform a valid one (INSERT, MODIFY OR DELETE".format(update[0].type))
                    return response

            # TODO: refactor.
            elif request_update.entity.HasField("register_entry"):

                # Verify if the user has permission to write into registers from the requested switch.
                if ConnectionArray.verifyPermission(context, switch, PermEnum.DEVICE_WRITE | PermEnum.RESOURCE_WRITE) is False:
                    ServerConfig.print_debug("Error: user does not have permission to write into registers from switch '{}'".format(switch.switch_name))
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User does not have permission to write into registers from switch '{}'".format(switch.switch_name))
                    return response

                register_id = request_update.entity.register_entry.register_id
                register = SwitchConf.getRegisterById(switch_id, register_id)

                result = p4_regs_api.reg_write(register.switch_id, register.reg_name, request_update.entity.register_entry.index.index, int(request_update.entity.register_entry.data.enum_value))
                return response

        return response

    @staticmethod
    def process_read_request(request, context):
        peer_key = context.peer()
        username = ConnectionArray.getUsername(peer_key)
        ServerConfig.print_debug("Received read request from {}({}):".format(peer_key, username))
        ServerConfig.print_debug(request)

        # Verify if the user is authenticated.
        if ConnectionArray.isAuthenticated(context.peer()) is False:
            user_name = ConnectionArray.getUsername(context.peer())
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("User '{}' is not authenticated".format(user_name))
            yield p4runtime_pb2.ReadResponse()
            return

        # Verify from which type of device to read.
        switch_id = request.device_id
        if switch_id == 0:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("PvS read methods are not implemented")
            yield p4runtime_pb2.ReadResponse()
            return

        # Search for the requested switch.
        try:
            switch = SwitchConf.switch_dict[switch_id]
        except KeyError:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Switch with id {} not found".format(switch_id))
            yield p4runtime_pb2.ReadResponse()
            return

        # Check every entity inside the request array.
        # If a requested entity is not found, an empty response is sent and the connection is closed.
        for entity in request.entities:

            if entity.HasField("table_entry"):

                # Verify if the user has permission to read table entries from the requested switch.
                if ConnectionArray.verifyPermission(context, switch, PermEnum.DEVICE_READ | PermEnum.FLOWRULE_READ) is False:
                    user_name = ConnectionArray.getUsername(context.peer())
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User '{}' does not have permission to read table entries from switch '{}'".format(user_name, switch.switch_name))
                    yield p4runtime_pb2.ReadResponse()
                    return

                (response, code, message) = RPC_mgmt.process_table_read(peer_key, username, switch, entity.table_entry)
                yield response
                if code is not grpc.StatusCode.OK:
                    context.set_code(code)
                    context.set_details(message)
                    return

            elif entity.HasField("register_entry"):

                # Verify if the user has permission to read registers from the requested switch.
                if ConnectionArray.verifyPermission(context, switch, PermEnum.DEVICE_READ | PermEnum.RESOURCE_READ) is False:
                    user_name = ConnectionArray.getUsername(context.peer())
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User '{}' does not have permission to read registers from switch '{}'".format(user_name, switch.switch_name))
                    yield p4runtime_pb2.ReadResponse()
                    return

                (response, code, message) = RPC_mgmt.process_register_read(switch_id, entity.register_entry)
                yield response
                if code is not grpc.StatusCode.OK:
                    context.set_code(code)
                    context.set_details(message)
                    return

            elif entity.HasField("counter_entry"):

                # Verify if the user has permission to read counters from the requested switch.
                if ConnectionArray.verifyPermission(context, switch, PermEnum.DEVICE_READ | PermEnum.RESOURCE_READ) is False:
                    user_name = ConnectionArray.getUsername(context.peer())
                    context.set_code(grpc.StatusCode.PERMISSION_DENIED)
                    context.set_details("User '{}' does not have permission to read counters from switch '{}'".format(user_name, switch.switch_name))
                    yield p4runtime_pb2.ReadResponse()
                    return

                (response, code, message) = RPC_mgmt.process_counter_read(switch_id, entity.counter_entry)
                yield response
                if code is not grpc.StatusCode.OK:
                    context.set_code(code)
                    context.set_details(message)
                    return

            else:
                context.set_code(grpc.StatusCode.UNIMPLEMENTED)
                context.set_details("Unsupported entity")
                yield p4runtime_pb2.ReadResponse()
                return

        return

    @staticmethod
    def process_table_read(peer_key, username, switch, entry):

        # Get the switch table object from the database.
        table_id = entry.table_id
        try:
            table = SwitchConf.table_dict[switch.switch_id, table_id]
        except KeyError:
            code = grpc.StatusCode.NOT_FOUND
            message = "Table with id {} not found".format(table_id)
            return (p4runtime_pb2.ReadResponse(), code, message)

        # Check the table type.
        match = entry.match[0]
        if not match.HasField("exact"):
            code = grpc.StatusCode.UNIMPLEMENTED
            message = "The requested table type is not supported"
            return (p4runtime_pb2.ReadResponse(), code, message)

        # Necessary match manipulations.
        match = entry.match[0]
        match_key = entry.match[0].exact.value
        match_key = re.sub('match_key', '[match_key]', match_key)
        match_key = match_key.split()
        match_key = ast.literal_eval(json.dumps(match_key))

        # Read the data from the requested table entry.
        ServerConfig.print_debug("Processing read request from {}({}) for table {}, switch {}".format(peer_key, username, table.table_name, switch.switch_name))
        (found, data) = p4_tables_api.table_cam_read_entry(switch, table, match_key)
        ServerConfig.print_debug("Entry found: {}, data: {}\n".format(found, data))

        # Create and fill the table read response.
        # Note that the action parameter id is hardcoded.
        response = p4runtime_pb2.ReadResponse()
        resp_entity = response.entities.add()
        resp_entity.table_entry.table_id = table.table_id

        resp_match = resp_entity.table_entry.match.add()
        resp_match.field_id = match.field_id
        resp_match.exact.value = match.exact.value

        bin_data = bin(int(data, 16))[2:]
        if len(bin_data) % 4:
            padding = 4 - (len(bin_data) % 4)
            bin_data = "0" * padding + bin_data

        resp_entity.table_entry.action.action.action_id = int(bin_data[0:4], 2)
        resp_action = resp_entity.table_entry.action.action.params.add()
        resp_action.param_id = 2
        resp_action.value = bin_data[4:]

        ServerConfig.print_debug(response)

        code = grpc.StatusCode.OK
        message = None
        return (response, code, message)

    @staticmethod
    def process_register_read(switch_id, entry):

        # Get the register object from the database.
        register_id = entry.register_id
        register = SwitchConf.getRegisterById(switch_id, register_id)
        if register is False:
           code = grpc.StatusCode.NOT_FOUND
           message = "Register with id {} not found".format(register_id)
           return (p4runtime_pb2.ReadResponse(), code, message)

        # TODO: finish this when testing is possible.
        ServerConfig.print_debug("Processing read request for register {} from switch id {}".format(register.reg_name, register.switch_id))
        data = p4_regs_api.reg_read(register.switch_id, register.reg_name, entry.index.index)
        if data is False:
            code = grpc.StatusCode.NOT_FOUND
            message = "Failed reading data from register '{}'".format(register.reg_name)
            return (p4runtime_pb2.ReadResponse(), code, message)

        # Create and fill the register read response.
        response = p4runtime_pb2.ReadResponse()
        resp_entity = response.entities.add()
        resp_entity.register_entry.register_id = register_id
        resp_entity.register_entry.index.index = entry.index.index
        resp_entity.register_entry.data.enum_value = bytes(data)

        code = grpc.StatusCode.OK
        message = None
        return (response, code, message)

    @staticmethod
    def process_counter_read(switch_id, entry):

        # Get the counter (register) object from the database.
        counter_id = entry.counter_id
        counter = SwitchConf.getRegisterById(switch_id, counter_id)
        if counter is False:
            code = grpc.StatusCode.NOT_FOUND
            message = "Counter with id {} not found".format(counter_id)
            return (p4runtime_pb2.ReadResponse(), code, message)

        ServerConfig.print_debug("Processing read request for counter {} from switch id {}".format(counter.reg_name, counter.switch_id))
        data = p4_regs_api.reg_read(counter.switch_id, counter.reg_name, entry.index.index)
        if data is False:
            code = grpc.StatusCode.NOT_FOUND
            message = "Failed reading data from counter '{}'".format(counter.reg_name)
            return (p4runtime_pb2.ReadResponse(), code, message)

        # Create and fill the counter read response.
        response = p4runtime_pb2.ReadResponse()
        resp_entity = response.entities.add()
        resp_entity.counter_entry.counter_id = counter_id + 10
        resp_entity.counter_entry.index.index = entry.index.index

        code = grpc.StatusCode.OK
        message = None
        return (response, code, message)
