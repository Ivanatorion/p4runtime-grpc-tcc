from DB_mgmt import *

from model.objects.SwitchObject import *
from model.objects.SwitchTableObject import *
from model.objects.SwitchTableActionObject import *
from model.objects.SwitchRegisterObject import *

import threading
lock = threading.Lock()

class SwitchConfDAO():

    @staticmethod
    def loadDbMemory(switch_dict, table_dict, table_action_dict):
        try:
            lock.acquire(True)
            # Load switches dictionary.
            queryCursor.execute("SELECT * FROM switches")
            switches = queryCursor.fetchall()
            for switch in switches:
                switch_dict[(switch[0])] = SwitchObject(switch[0], switch[1], switch[2], pvs_dir_path = switch[3], bmv2_address = switch[4])

            # Load tables dictionary.
            queryCursor.execute("SELECT * FROM switch_tables")
            tables = queryCursor.fetchall()
            for table in tables:
                table_dict[(table[0], table[1])] = SwitchTableObject(table[0], table[1], table[2], table[3], table[4])
                queryCursor.execute("SELECT field_name, field_size FROM table_match_fields WHERE device_id=? AND table_id=?", (table[0], table[1]))
                fields = queryCursor.fetchall()
                for field in fields:
                    table_dict[(table[0], table[1])].match_fields.append(field)

            # Load actions dictionary.
            queryCursor.execute("SELECT * FROM table_actions")
            actions = queryCursor.fetchall()
            for action in actions:
                table_action_dict[(action[0], action[1], action[2])] = SwitchTableActionObject(action[0], action[1], action[2], action[3])
                queryCursor.execute("SELECT field_name, field_size FROM table_action_fields WHERE device_id=? AND table_id=? AND action_id=?", (action[0], action[1], action[2]))
                fields = queryCursor.fetchall()
                for field in fields:
                    table_action_dict[(action[0], action[1], action[2])].action_fields.append(field)

            print "Successfully loaded switches and tables database into memory"
            return True
        finally:
            lock.release()

    @staticmethod
    def addSwitch(dict, switch_id, switch_name, switch_type, pvs_dir_path, bmv2_address):
        try:
            lock.acquire(True)
            try:
                queryCursor.execute("INSERT INTO switches (device_id, switch_name, switch_type, pvs_dir_path, bmv2_address) VALUES (?, ?, ?, ?, ?)", (switch_id, switch_name, switch_type, pvs_dir_path, bmv2_address))
                dbVar.commit()
                dict[(switch_id)] = SwitchObject(switch_id, switch_name, switch_type, pvs_dir_path=pvs_dir_path, bmv2_address=bmv2_address)
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def addTable(dict, switch_id, table_id, table_name, match_type, table_base_address):
        try:
            lock.acquire(True)
            if switch_id == -1:
                return False

            # Check if the switch already has a table named "table_name".
            queryCursor.execute("SELECT * FROM switch_tables WHERE table_id=? AND device_id=?", (table_id, switch_id))
            if queryCursor.fetchone() is not None:
                return False

            try:
                queryCursor.execute("INSERT INTO switch_tables (device_id, table_id, table_name, match_type, base_address) VALUES (?,?,?,?,?)", (switch_id, table_id, table_name, match_type, table_base_address))
                dbVar.commit()
                dict[(switch_id, table_id)] = SwitchTableObject(switch_id, table_id, table_name, match_type, table_base_address)
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def addTableMatchField(dict, switch_id, table_id, field_id, field_name, field_type, field_size):
        try:
            lock.acquire(True)
            if switch_id == -1:
                return False

            # Get the table id.
            queryCursor.execute("SELECT * FROM switch_tables WHERE table_id=? AND device_id=?", (table_id, switch_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            table_id = row[1]

            # Check if the table already has a field named "field_name".
            queryCursor.execute("SELECT * FROM table_match_fields WHERE field_name=? AND device_id=? AND table_id=?", (field_name, switch_id, table_id))
            if queryCursor.fetchone() is not None:
                return False

            try:
                queryCursor.execute("INSERT INTO table_match_fields (device_id, table_id, field_id, field_name, field_type, field_size) VALUES (?,?,?,?,?,?)", (switch_id, table_id, field_id, field_name, field_type, field_size))
                dbVar.commit()
                dict[(switch_id, table_id)].match_fields.append((field_name, field_size))
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def addTableAction(dict, switch_id, table_id, action_id, action_name):
        try:
            lock.acquire(True)
            if switch_id == -1:
                return False

            # Get the table id.
            queryCursor.execute("SELECT * FROM switch_tables WHERE table_id=? AND device_id=?", (table_id, switch_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            table_id = row[1]

            # Check if the table already has an action named "action_name".
            queryCursor.execute("SELECT * FROM table_actions WHERE action_id=? AND device_id=? AND table_id=?", (action_id, switch_id, action_id))
            if queryCursor.fetchone() is not None:
                return False

            try:
                queryCursor.execute("INSERT INTO table_actions (device_id, table_id, action_id, action_name) VALUES (?,?,?,?)", (switch_id, table_id, action_id, action_name))
                dbVar.commit()
                dict[(switch_id, table_id, action_id)] = SwitchTableActionObject(switch_id, table_id, action_id, action_name)
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def addTableActionField(dict, switch_id, table_id, action_id, field_id, field_name, field_type, field_size):
        try:
            lock.acquire(True)
            if switch_id == -1:
                return False

            # Get the table id.
            queryCursor.execute("SELECT * FROM switch_tables WHERE table_id=? AND device_id=?", (table_id, switch_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            table_id = row[1]

            # Check if the table already has an field named "field_name".
            queryCursor.execute("SELECT * FROM table_action_fields WHERE device_id=? AND table_id=? AND action_id=? AND field_id=?", (switch_id, table_id, action_id, field_id))
            if queryCursor.fetchone() is not None:
                return False

            try:
                queryCursor.execute("INSERT INTO table_action_fields (device_id, table_id, action_id, field_id, field_name, field_type, field_size) VALUES (?,?,?,?,?,?,?)", (switch_id, table_id, action_id, field_id, field_name, field_type, field_size))
                dbVar.commit()
                dict[(switch_id, table_id, action_id)].action_fields.append((field_name, field_size))
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def addRegister(switch_id, reg_id, reg_name):

        try:
            lock.acquire(True)
            # To be consistent with the other methods.
            if switch_id == -1:
                return False

            # Check if the switch already has a register named "reg_name" in the database.
            queryCursor.execute("SELECT * FROM switch_registers WHERE device_id=? AND reg_id=?", (switch_id, reg_id))
            if queryCursor.fetchone() is not None:
                return False

            # Add the new register into the database.
            try:
                queryCursor.execute("INSERT INTO switch_registers (device_id, reg_id, reg_name) VALUES (?,?,?)", (switch_id, reg_id, reg_name))
                dbVar.commit()
                return True
            except:
                return False
        finally:
            lock.release()

    @staticmethod
    def getSwitchByName(switch_name):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, switch_name, switch_type, pvs_dir_path, bmv2_address FROM switches WHERE switch_name=?", (switch_name,))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchObject(row[0], row[1], row[2], pvs_dir_path=row[3], bmv2_address=row[4])
        finally:
            lock.release()

    @staticmethod
    def getSwitchById(switch_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, switch_name, switch_type, pvs_dir_path, bmv2_address FROM switches WHERE device_id=?", (switch_id,))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchObject(row[0], row[1], row[2], pvs_dir_path=row[3], bmv2_address=row[4])
        finally:
            lock.release()

    @staticmethod
    def getRegisterById(switch_id, reg_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, reg_id, reg_name FROM switch_registers WHERE device_id=? AND reg_id=?", (switch_id, reg_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchRegisterObject(row[0], row[1], row[2])
        finally:
            lock.release()

    @staticmethod
    def getRegisterByName(switch_id, reg_name):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, reg_id, reg_name FROM switch_registers WHERE device_id=? AND reg_name=?", (switch_id, reg_name))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchRegisterObject(row[0], row[1], row[2])
        finally:
            lock.release()

    @staticmethod
    def getSwitchTableById(switch_id, table_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, table_id, table_name, match_type, base_address FROM switch_tables WHERE table_id=? AND device_id=?", (table_id, switch_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchTableObject(row[0], row[1], row[2], row[3], row[4])
        finally:
            lock.release()

    @staticmethod
    def getSwitchTableByName(switch_id, table_name):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT device_id, table_id, table_name, match_type, base_address FROM switch_tables WHERE table_name=? AND device_id=?", (table_name, switch_id))
            row = queryCursor.fetchone()
            if row is None:
                return False
            else:
                return SwitchTableObject(row[0], row[1], row[2], row[3], row[4])
        finally:
            lock.release()

    @staticmethod
    def getTableMatchFieldName(switch_id, table_id, field_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT field_name FROM table_match_fields WHERE table_id=? AND device_id=? AND field_id=?", (table_id, switch_id, field_id))
            row = queryCursor.fetchone()
            return row[0]
        finally:
            lock.release()

    @staticmethod
    def getTableMatchFields(switch_id, table_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT field_name, field_type, field_size FROM table_match_fields WHERE table_id=? AND device_id=?", (table_id, switch_id))
            row = queryCursor.fetchall()
            return row
        finally:
            lock.release()

    @staticmethod
    def getTableActionName(switch_id, table_id, action_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT action_name FROM table_actions WHERE table_id=? AND device_id=? AND action_id=?", (table_id, switch_id, action_id))
            row = queryCursor.fetchone()
            return row[0]
        finally:
            lock.release()

    @staticmethod
    def getTableActionId(switch_id, table_id, action_name):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT action_id FROM table_actions WHERE device_id=? AND table_id=? AND action_name=?", (switch_id, table_id, action_name))
            row = queryCursor.fetchone()
            return row[0]
        finally:
            lock.release()

    @staticmethod
    def getTableActionFields(switch_id, table_id, action_id):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT field_name, field_type, field_size FROM table_action_fields WHERE table_id=? AND device_id=? AND action_id=?", (table_id, switch_id, action_id))
            row = queryCursor.fetchall()
            return row
        finally:
            lock.release()

    @staticmethod
    def hasTableActionName(switch_id, table_id, action_name):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT * FROM table_actions WHERE device_id=? AND table_id=? AND action_name=?", (switch_id, table_id, action_name))
            row = queryCursor.fetchall()
            if len(row) == 0:
                return False
            else:
                return True
        finally:
            lock.release()

    @staticmethod
    def hasTableMatchType(switch_id, table_match_type):
        try:
            lock.acquire(True)
            queryCursor.execute("SELECT table_id FROM switch_tables WHERE device_id=? AND match_type=?", (switch_id, table_match_type))
            row = queryCursor.fetchall()
            if len(row) == 0:
                return False
            else:
                return True
        finally:
            lock.release()

    @staticmethod
    def getAllSwitchTables():
        try:
            lock.acquire(True)
            return queryCursor.execute("SELECT * FROM switch_tables").fetchall()
        finally:
            lock.release()

    @staticmethod
    def getAllSwitchNames():
        try:
            lock.acquire(True)
            return queryCursor.execute("SELECT switch_name FROM switches").fetchall()
        finally:
            lock.release()

    @staticmethod
    def getAllSwitchIDs():
        try:
            lock.acquire(True)
            return queryCursor.execute("SELECT device_id FROM switches").fetchall()
        finally:
            lock.release()
