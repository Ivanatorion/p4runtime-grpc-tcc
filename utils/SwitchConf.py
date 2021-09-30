from model.SwitchConfDAO import *

from model.objects.SwitchObject import *
from model.objects.SwitchTableObject import *
from model.objects.SwitchTableActionObject import *

class SwitchConf():

    # Dictionaries to hold every object type and avoid database accesses.
    switch_dict = {}              # key: (switch_id)
    table_dict = {}               # key: (switch_id, table_id)
    table_action_dict = {}        # key: (switch_id, table_id, action_id)

    @staticmethod
    def loadDbMemory():
        return SwitchConfDAO.loadDbMemory(SwitchConf.switch_dict, SwitchConf.table_dict, SwitchConf.table_action_dict)

    @staticmethod
    def addSwitch(switch_id, switch_name, switch_type, dir_path, bmv2_address):
        return SwitchConfDAO.addSwitch(SwitchConf.switch_dict, switch_id, switch_name, switch_type, dir_path, bmv2_address)

    @staticmethod
    def addTable(switch_id, table_id, table_name, match_type, table_base_address):
        return SwitchConfDAO.addTable(SwitchConf.table_dict, switch_id, table_id, table_name, match_type, table_base_address)

    @staticmethod
    def addTableMatchField(switch_id, table_id, field_id, field_name, field_type, field_size):
        return SwitchConfDAO.addTableMatchField(SwitchConf.table_dict, switch_id, table_id, field_id, field_name, field_type, field_size)

    @staticmethod
    def addTableAction(switch_id, table_id, action_id, action_name):
        return SwitchConfDAO.addTableAction(SwitchConf.table_action_dict, switch_id, table_id, action_id, action_name)

    @staticmethod
    def addTableActionField(switch_id, table_id, action_id, field_id, field_name, field_type, field_size):
        return SwitchConfDAO.addTableActionField(SwitchConf.table_action_dict, switch_id, table_id, action_id, field_id, field_name, field_type, field_size)

    @staticmethod
    def addRegister(switch_id, reg_id, reg_name):
        return SwitchConfDAO.addRegister(switch_id, reg_id, reg_name)

    @staticmethod
    def getSwitchByName(switch_name):
        return SwitchConfDAO.getSwitchByName(switch_name)

    @staticmethod
    def getSwitchById(switch_id):
        try:
            switch = SwitchConf.switch_dict[switch_id]
            return switch
        except KeyError:
            switch = SwitchConfDAO.getSwitchById(switch_id)
            SwitchConf.switch_dict[switch_id] = switch
            return switch

    @staticmethod
    def getRegisterById(switch_id, reg_id):
        return SwitchConfDAO.getRegisterById(switch_id, reg_id)

    @staticmethod
    def getRegisterByName(switch_id, reg_name):
        return SwitchConfDAO.getRegisterByName(switch_id, reg_name)

    @staticmethod
    def getSwitchTableByName(switch_id, table_name):
        return SwitchConfDAO.getSwitchTableByName(switch_id, table_name)

    @staticmethod
    def getSwitchTableById(switch_id, table_id):
        try:
            table = SwitchConf.table_dict[switch_id, table_id]
            return table
        except KeyError:
            table = SwitchConfDAO.getSwitchTableById(switch_id, table_id)
            SwitchConf.table_dict[switch_id, table_id] = table
            return table

    @staticmethod
    def getTableMatchFields(switch_id, table_id):
        return SwitchConfDAO.getTableMatchFields(switch_id, table_id)

    @staticmethod
    def getTableMatchFieldName(switch_id, table_id, field_id):
        return SwitchConfDAO.getTableMatchFieldName(switch_id, table_id, field_id)

    @staticmethod
    def getTableActionName(switch_id, table_id, action_id):
        return SwitchConfDAO.getTableActionName(switch_id, table_id, action_id)

    @staticmethod
    def getTableActionId(switch_id, table_id, action_name):
        return SwitchConfDAO.getTableActionId(switch_id, table_id, action_name)

    @staticmethod
    def getTableActionFields(switch_id, table_id, action_id):
        return SwitchConfDAO.getTableActionFields(switch_id, table_id, action_id)

    @staticmethod
    def hasTableActionName(switch_id, table_id, action_name):
        return SwitchConfDAO.hasTableActionName(switch_id, table_id, action_name)

    @staticmethod
    def hasTableMatchType(switch_id, table_match_type):
        return SwitchConfDAO.hasTableMatchType(switch_id, table_match_type)

    @staticmethod
    def getAllSwitchTables():
        return SwitchConfDAO.getAllSwitchTables()

    @staticmethod
    def getAllSwitchNames():
        return SwitchConfDAO.getAllSwitchNames()

    @staticmethod
    def getAllSwitchIDs():
        return SwitchConfDAO.getAllSwitchIDs()
