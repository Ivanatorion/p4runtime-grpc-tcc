import sqlite3
import json
import unicodedata

dbVar = sqlite3.connect("database.db", check_same_thread=False)

queryCursor = dbVar.cursor()

class DB_mgmt():

    @staticmethod
    def initDB():
        queryCursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='switches'")
        if queryCursor.fetchone() is not None :
            return True
        else:
            DB_mgmt.createTables()
            return True

    @staticmethod
    def dropAllTables():
        queryCursor.execute("DROP TABLE IF EXISTS switches")
        queryCursor.execute("DROP TABLE IF EXISTS switch_tables")
        queryCursor.execute("DROP TABLE IF EXISTS switch_registers")
        queryCursor.execute("DROP TABLE IF EXISTS table_match_fields")
        queryCursor.execute("DROP TABLE IF EXISTS table_actions")
        queryCursor.execute("DROP TABLE IF EXISTS table_action_fields")
        queryCursor.execute("DROP TABLE IF EXISTS users")
        queryCursor.execute("DROP TABLE IF EXISTS permissions")
        queryCursor.execute("DROP TABLE IF EXISTS policies")
        return

    # Create the database tables.
    @staticmethod
    def createTables():
        try:
            queryCursor.execute("CREATE TABLE switches (device_id INTEGER PRIMARY KEY, switch_name TEXT UNIQUE, switch_type INTEGER, pvs_dir_path TEXT, bmv2_address TEXT)")
            queryCursor.execute("CREATE TABLE switch_tables (device_id INTEGER, table_id INTEGER, table_name TEXT, match_type TEXT, base_address INTEGER,  FOREIGN KEY(device_id) REFERENCES switches(device_id), PRIMARY KEY (device_id, table_id))")
            queryCursor.execute("CREATE TABLE switch_registers (device_id INTEGER, reg_id INTEGER, reg_name TEXT, FOREIGN KEY(device_id) REFERENCES switches(device_id), PRIMARY KEY (device_id, reg_id))")
            queryCursor.execute("CREATE TABLE table_match_fields (device_id INTEGER, table_id INTEGER, field_id INTEGER, field_name TEXT, field_type TEXT, field_size INTEGER, FOREIGN KEY(device_id) REFERENCES switches(device_id), FOREIGN KEY(table_id) REFERENCES switch_tables(table_id), PRIMARY KEY (device_id, table_id, field_id))")
            queryCursor.execute("CREATE TABLE table_actions (device_id INTEGER, table_id INTEGER, action_id INTEGER, action_name TEXT, FOREIGN KEY(device_id) REFERENCES switches(device_id), FOREIGN KEY(table_id) REFERENCES switch_tables(table_id), PRIMARY KEY (device_id, table_id, action_id))")
            queryCursor.execute("CREATE TABLE table_action_fields (device_id INTEGER, table_id INTEGER, action_id INTEGER, field_id INTEGER, field_name TEXT, field_type TEXT, field_size INTEGER, FOREIGN KEY(device_id) REFERENCES switches(device_id), FOREIGN KEY(table_id) REFERENCES switch_tables(table_id), FOREIGN KEY(action_id) REFERENCES table_actions(action_id), PRIMARY KEY (device_id, table_id, action_id, field_id))")
            queryCursor.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT UNIQUE, password TEXT)")
            queryCursor.execute("CREATE TABLE permissions (user_id INTEGER, device_id INTEGER, perms INTEGER, FOREIGN KEY(device_id) REFERENCES switches(device_id), FOREIGN KEY(user_id) REFERENCES users(user_id), PRIMARY KEY (user_id, device_id))")
            queryCursor.execute("CREATE TABLE policies (perms_needed INTERGER PRIMARY KEY, perms_granted INTEGER, ifc_response INTEGER, ifc_message TEXT)")
        except:
            return False
        return True
