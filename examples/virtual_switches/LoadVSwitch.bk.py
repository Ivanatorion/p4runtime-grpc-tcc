import os

from utils.SM_mgmt import *
from config.PermEnum import *
from config.SwitchTypeEnum import *

class LoadVSwitch():

	@staticmethod
	def load_switches():
		SM_mgmt.init_database()
		SM_mgmt.load_libsume_module("platform_api/lib/hwtestlib/libsume.so")

		Auth.addUser("admin", "admin")
		Auth.addUser("ivan1", "ivan1")
		Auth.addUser("ivan1_admin", "ivan1_admin")

		Auth.addPol(VIFC_DEVICE, VIFC_PACKET, VIFC_RESPONSE_WARN, "Source has DEVICE therefore it is granted PACKET")

		switch_id = 1;

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading l2 switch (id: {}), modules @ platform_api/lib/l2/, switch_data @ platform_api/lib/l2/switch_info.dat".format(switch_id)
			SM_mgmt.create_switch_data(switch_id, "l2", TYPE_BMV2, "platform_api/lib/l2/switch_info.dat", "platform_api/lib/l2/table_defines.json", pvs_dir_path="platform_api/lib/l2/", bmv2_address="127.0.0.1:50052")

			Auth.addPermission("admin", "l2", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("ivan1", "l2", DEVICE_EVENT | PACKET_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("ivan1_admin", "l2", DEVICE_EVENT | PACKET_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		SM_mgmt.load_switch_modules(switch_id)
		SM_mgmt.load_reg_data(switch_id)
		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading router switch (id: {}), modules @ platform_api/lib/router/, switch_data @ platform_api/lib/router/switch_info.dat".format(switch_id)
			SM_mgmt.create_switch_data(switch_id, "router", TYPE_BMV2, "platform_api/lib/router/switch_info.dat", "platform_api/lib/router/table_defines.json", pvs_dir_path="platform_api/lib/router/", bmv2_address="127.0.0.1:50053")

			Auth.addPermission("admin", "router", DEVICE_EVENT | PACKET_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("ivan1", "router", DEVICE_EVENT | PACKET_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("ivan1_admin", "router", DEVICE_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		SM_mgmt.load_switch_modules(switch_id)
		SM_mgmt.load_reg_data(switch_id)
		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading int switch (id: {}), modules @ platform_api/lib/int/, switch_data @ platform_api/lib/int/switch_info.dat".format(switch_id)
			SM_mgmt.create_switch_data(switch_id, "int", TYPE_BMV2, "platform_api/lib/int/switch_info.dat", "platform_api/lib/int/table_defines.json", pvs_dir_path="platform_api/lib/int/", bmv2_address="127.0.0.1:50054")

			Auth.addPermission("admin", "int", DEVICE_EVENT | PACKET_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("ivan1_admin", "int", DEVICE_EVENT | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		SM_mgmt.load_switch_modules(switch_id)
		SM_mgmt.load_reg_data(switch_id)
		switch_id += 1
