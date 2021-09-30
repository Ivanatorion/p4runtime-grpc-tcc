import os

from utils.SM_mgmt import *
from config.PermEnum import *
from config.SwitchTypeEnum import *

class LoadVSwitch():

	@staticmethod
	def load_switches():
		SM_mgmt.init_database()
		SM_mgmt.load_libsume_module("platform_api/lib/hwtestlib/libsume.so")

		Auth.addUser("ivan1", "ivan1")
		Auth.addUser("admin", "admin")

		switch_id = 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s1"
			SM_mgmt.create_switch_data(switch_id, "l2-1", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50052")

			Auth.addPermission("ivan1", "l2-1", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)
			Auth.addPermission("admin", "l2-1", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s2"
			SM_mgmt.create_switch_data(switch_id, "l2-2", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50053")

			Auth.addPermission("admin", "l2-2", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s3"
			SM_mgmt.create_switch_data(switch_id, "l2-3", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50054")

			Auth.addPermission("admin", "l2-3", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s4"
			SM_mgmt.create_switch_data(switch_id, "l2-4", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50055")

			Auth.addPermission("admin", "l2-4", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s5"
			SM_mgmt.create_switch_data(switch_id, "l2-5", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50056")

			Auth.addPermission("admin", "l2-5", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s6"
			SM_mgmt.create_switch_data(switch_id, "l2-6", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50057")

			Auth.addPermission("admin", "l2-6", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s7"
			SM_mgmt.create_switch_data(switch_id, "l2-7", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50058")

			Auth.addPermission("admin", "l2-7", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s8"
			SM_mgmt.create_switch_data(switch_id, "l2-8", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50059")

			Auth.addPermission("admin", "l2-8", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s9"
			SM_mgmt.create_switch_data(switch_id, "l2-9", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50060")

			Auth.addPermission("admin", "l2-9", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s10"
			SM_mgmt.create_switch_data(switch_id, "l2-10", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50061")

			Auth.addPermission("admin", "l2-10", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s11"
			SM_mgmt.create_switch_data(switch_id, "l2-11", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50062")

			Auth.addPermission("admin", "l2-11", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s12"
			SM_mgmt.create_switch_data(switch_id, "l2-12", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50063")

			Auth.addPermission("admin", "l2-12", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s13"
			SM_mgmt.create_switch_data(switch_id, "l2-13", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50064")

			Auth.addPermission("admin", "l2-13", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s14"
			SM_mgmt.create_switch_data(switch_id, "l2-14", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50065")

			Auth.addPermission("admin", "l2-14", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s15"
			SM_mgmt.create_switch_data(switch_id, "l2-15", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50066")

			Auth.addPermission("admin", "l2-15", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s16"
			SM_mgmt.create_switch_data(switch_id, "l2-16", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50067")

			Auth.addPermission("admin", "l2-16", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s17"
			SM_mgmt.create_switch_data(switch_id, "l2-17", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50068")

			Auth.addPermission("admin", "l2-17", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s18"
			SM_mgmt.create_switch_data(switch_id, "l2-18", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50069")

			Auth.addPermission("admin", "l2-18", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s19"
			SM_mgmt.create_switch_data(switch_id, "l2-19", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50070")

			Auth.addPermission("admin", "l2-19", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s20"
			SM_mgmt.create_switch_data(switch_id, "l2-20", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50071")

			Auth.addPermission("admin", "l2-20", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s21"
			SM_mgmt.create_switch_data(switch_id, "l2-21", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50072")

			Auth.addPermission("admin", "l2-21", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s22"
			SM_mgmt.create_switch_data(switch_id, "l2-22", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50073")

			Auth.addPermission("admin", "l2-22", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s23"
			SM_mgmt.create_switch_data(switch_id, "l2-23", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50074")

			Auth.addPermission("admin", "l2-23", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s24"
			SM_mgmt.create_switch_data(switch_id, "l2-24", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50075")

			Auth.addPermission("admin", "l2-24", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s25"
			SM_mgmt.create_switch_data(switch_id, "l2-25", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50076")

			Auth.addPermission("admin", "l2-25", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s26"
			SM_mgmt.create_switch_data(switch_id, "l2-26", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50077")

			Auth.addPermission("admin", "l2-26", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s27"
			SM_mgmt.create_switch_data(switch_id, "l2-27", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50078")

			Auth.addPermission("admin", "l2-27", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s28"
			SM_mgmt.create_switch_data(switch_id, "l2-28", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50079")

			Auth.addPermission("admin", "l2-28", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s29"
			SM_mgmt.create_switch_data(switch_id, "l2-29", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50080")

			Auth.addPermission("admin", "l2-29", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s30"
			SM_mgmt.create_switch_data(switch_id, "l2-30", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50081")

			Auth.addPermission("admin", "l2-30", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s31"
			SM_mgmt.create_switch_data(switch_id, "l2-31", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50082")

			Auth.addPermission("admin", "l2-31", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s32"
			SM_mgmt.create_switch_data(switch_id, "l2-32", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50083")

			Auth.addPermission("admin", "l2-32", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s33"
			SM_mgmt.create_switch_data(switch_id, "l2-33", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50084")

			Auth.addPermission("admin", "l2-33", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s34"
			SM_mgmt.create_switch_data(switch_id, "l2-34", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50085")

			Auth.addPermission("admin", "l2-34", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s35"
			SM_mgmt.create_switch_data(switch_id, "l2-35", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50086")

			Auth.addPermission("admin", "l2-35", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s36"
			SM_mgmt.create_switch_data(switch_id, "l2-36", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50087")

			Auth.addPermission("admin", "l2-36", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s37"
			SM_mgmt.create_switch_data(switch_id, "l2-37", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50088")

			Auth.addPermission("admin", "l2-37", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s38"
			SM_mgmt.create_switch_data(switch_id, "l2-38", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50089")

			Auth.addPermission("admin", "l2-38", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s39"
			SM_mgmt.create_switch_data(switch_id, "l2-39", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50090")

			Auth.addPermission("admin", "l2-39", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s40"
			SM_mgmt.create_switch_data(switch_id, "l2-40", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50091")

			Auth.addPermission("admin", "l2-40", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s41"
			SM_mgmt.create_switch_data(switch_id, "l2-41", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50092")

			Auth.addPermission("admin", "l2-41", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s42"
			SM_mgmt.create_switch_data(switch_id, "l2-42", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50093")

			Auth.addPermission("admin", "l2-42", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s43"
			SM_mgmt.create_switch_data(switch_id, "l2-43", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50094")

			Auth.addPermission("admin", "l2-43", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s44"
			SM_mgmt.create_switch_data(switch_id, "l2-44", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50095")

			Auth.addPermission("admin", "l2-44", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s45"
			SM_mgmt.create_switch_data(switch_id, "l2-45", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50096")

			Auth.addPermission("admin", "l2-45", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s46"
			SM_mgmt.create_switch_data(switch_id, "l2-46", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50097")

			Auth.addPermission("admin", "l2-46", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s47"
			SM_mgmt.create_switch_data(switch_id, "l2-47", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50098")

			Auth.addPermission("admin", "l2-47", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s48"
			SM_mgmt.create_switch_data(switch_id, "l2-48", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50099")

			Auth.addPermission("admin", "l2-48", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s49"
			SM_mgmt.create_switch_data(switch_id, "l2-49", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50100")

			Auth.addPermission("admin", "l2-49", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s50"
			SM_mgmt.create_switch_data(switch_id, "l2-50", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50101")

			Auth.addPermission("admin", "l2-50", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1

		if (SwitchConf.getSwitchById(switch_id) == False):
			print "Loading s51"
			SM_mgmt.create_switch_data(switch_id, "l2-51", TYPE_BMV2, "", "", bmv2_address="127.0.0.1:50102")

			Auth.addPermission("admin", "l2-51", DEVICE_EVENT | PACKET_EVENT | PACKET_READ | PACKET_WRITE | DEVICE_WRITE | FLOWRULE_WRITE | RESOURCE_WRITE | DEVICE_READ | FLOWRULE_READ | RESOURCE_READ)

		switch_id += 1
