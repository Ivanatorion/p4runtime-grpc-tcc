import socket
import grpc
import time
from datetime import datetime

from p4.v1 import p4runtime_pb2 as p4runtime_pb2

from bmv2_module import p4runtime_lib
from bmv2_module.p4runtime_lib import bmv2
from bmv2_module.p4runtime_lib.error_utils import printGrpcError
from bmv2_module.p4runtime_lib.switch import ShutdownAllSwitchConnections

from SwitchConf import *

class BMV2_connection():

    @staticmethod
    def process_write_bmv2(request):
        response = request
        print request

        switch = SwitchConf.getSwitchById(request.device_id)
        if switch == False:
            print "Device with ID %d not found" % request.device_id
            return response

        switch_bmv2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
             name=switch.switch_name,
             address=switch.bmv2_address,
             device_id=switch.switch_id)

        try:
            switch_bmv2.MasterArbitrationUpdate()
            switch_bmv2.WriteFlowRule(request)

            print "Write Request was made successfully"
        except grpc.RpcError as e:
                err_message = printGrpcError(e)
                print err_message
                if err_message != None and ("Match entry exists" in err_message):
                    request.updates[0].type = p4runtime_pb2.Update.MODIFY
                    switch_bmv2.WriteFlowRule(request)
                    print "Writing request with MODIFY instead was sucessfull"
                else:
                    print "Write request failed!"

        ShutdownAllSwitchConnections()
        return response
