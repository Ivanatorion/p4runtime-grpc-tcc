#!/usr/bin/env python

#
# Copyright (c) 2015 University of Cambridge
# All rights reserved.
#
# This software was developed by Stanford University and the University of Cambridge Computer Laboratory
# under National Science Foundation under Grant No. CNS-0855268,
# the University of Cambridge Computer Laboratory under EPSRC INTERNET Project EP/H040536/1 and
# by the University of Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-11-C-0249 ("MRC2"),
# as part of the DARPA MRC research programme.
#
# @NETFPGA_LICENSE_HEADER_START@
#
# Licensed to NetFPGA C.I.C. (NetFPGA) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  NetFPGA licenses this
# file to you under the NetFPGA Hardware-Software License, Version 1.0 (the
# "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#   http://www.netfpga-cic.org
#
# Unless required by applicable law or agreed to in writing, Work distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.
#
# @NETFPGA_LICENSE_HEADER_END@
#
# This code was modified for use in PvS: Programmable Virtual Switches
# Copyright (c) 2020 <authors>
# All rights reserved.

from fcntl import *
from ctypes import *

from config import ServerConfig

# libsume module loaded on server startup.
libsume = None

p4_externs_dict = {}

def get_address(switch_id, reg_name, index):

    # cond = reg_name not in p4_externs_dict[switch_id].keys() or "control_width" not in p4_externs_dict[switch_id][reg_name].keys() or p4_externs_dict[switch_id][reg_name]["control_width"] < 0

    if reg_name not in p4_externs_dict[switch_id].keys():
        ServerConfig.print_debug("Failed getting register read address: register {} not found".format(reg_name))
        return False
        
    if "control_width" not in p4_externs_dict[switch_id][reg_name].keys():
        ServerConfig.print_debug("Failed getting register read address: register {} does not have 'control_width' field".format(reg_name))
        return False

    if p4_externs_dict[switch_id][reg_name]["control_width"] < 0:
        ServerConfig.print_debug("Failed getting register read address: register {} has negative 'control_width' field".format(reg_name))
        return False

    # This is handled differently from the original API.
    if "base_addr" not in p4_externs_dict[switch_id][reg_name].keys():
        ServerConfig.print_debug("Failed getting register read address: register {} does not have 'base_addr' field".format(reg_name))
        return False

    addressable_depth = 2 ** p4_externs_dict[switch_id][reg_name]["control_width"]
    if index >= addressable_depth or index < 0:
        ServerConfig.print_debug("Failed getting register read address: index {}[{}] out of bounds".format(reg_name, index))
        return False

    return p4_externs_dict[switch_id][reg_name]["base_addr"] + index

#####################
### API Functions ###
#####################

def reg_read(switch_id, reg_name, index):

    if switch_id not in p4_externs_dict:
        ServerConfig.print_debug("Failed reading register: switch id {} not found in p4_externs_dict".format(switch_id))
        return False

    # print "REGISTERS FROM SWITCH ID {}: {}\n".format(switch_id, p4_externs_dict[switch_id].keys())
    # print "KEYS FROM '{}' REGISTER: {}\n".format(reg_name, p4_externs_dict[switch_id][reg_name].keys())
    # print "CONTROL WIDTH FOR REGISTER '{}': {}\n".format(reg_name, p4_externs_dict[switch_id][reg_name]["control_width"])

    address = get_address(switch_id, reg_name, index)
    # print "READ ADDRESS: {}\n".format(address)

    return libsume.regread(address) if address != False else False

def reg_write(switch_id, reg_name, index, value):

    if switch_id not in p4_externs_dict:
        ServerConfig.print_debug("Failed reading register: switch id {} not found in p4_externs_dict".format(switch_id))
        return False

    address = get_address(switch_id, reg_name, index)
    return libsume.regwrite(address, value) if address != False else False
