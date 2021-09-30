from DB_mgmt import *
from protobuffs.code_pb2 import *

from model.objects.User import *

class AuthDAO():

    # Load the permission database into an in-memory dictionary.
    # This method also initializes objects for users with no previous permissions.
    @staticmethod
    def loadDbMemory(memory_db):

        # Get every switch id and every user id stored in the database.
        queryCursor.execute("SELECT device_id FROM switches")
        switch_ids = queryCursor.fetchall()
        queryCursor.execute("SELECT user_id FROM users")
        user_ids = queryCursor.fetchall()

        # Initialize the in-memory dictionary.
        for user_id in user_ids:
            for switch_id in switch_ids:
                key = (user_id[0], switch_id[0])
                if key not in memory_db:
                    queryCursor.execute("SELECT perms FROM permissions WHERE user_id=? AND device_id=?", key)
                    permission = queryCursor.fetchone()
                    memory_db[key] = 0x0000000 if permission is None else permission[0]

        print "Successfully loaded permission database into memory"
        return

    @staticmethod
    def addUser(user_name, password):
        try:
            queryCursor.execute("INSERT INTO users (name, password) VALUES (?,?)", (user_name, password))
            dbVar.commit()
            return True
        except:
            #print "Failed adding user '{}': could not commit to the database".format(user_name)
            return False

    @staticmethod
    def addPol(needs, receives, response, message):
        queryCursor.execute("SELECT perms_granted FROM policies WHERE perms_needed=?", (needs,))
        stored_pol = queryCursor.fetchone()
        if stored_pol is None:
            try:
                queryCursor.execute("INSERT INTO policies (perms_needed, perms_granted, ifc_response, ifc_message) VALUES (?,?,?,?)", (needs, receives, response, message))
                dbVar.commit()
                return True
            except:
                #print "Failed adding pol '{} {}': could not commit to the database".format(needs, receives)
                return False
        else:
            receives = receives | stored_pol[0]
            try:
                queryCursor.execute("UPDATE policies SET perms_granted=? WHERE perms_needed=?", (receives, needs))
                dbVar.commit()
                return True
            except:
                #print "Failed adding pol '{} {}': could not commit to the database".format(needs, receives)
                return False

    @staticmethod
    def getUserByName(user_name):
        queryCursor.execute("SELECT user_id, name FROM users WHERE name=?", (user_name,))
        user_data = queryCursor.fetchone()
        if user_data is None:
            return False
        else:
            return User(user_data[0], user_data[1])

    @staticmethod
    def getUserPermissions(user_name):
        user = AuthDAO.getUserByName(user_name)
        if user is False:
            #print "Failed getting permissions: user '{}' not found".format(user_name)
            return False
        else:
            queryCursor.execute("SELECT perms FROM permissions WHERE user_id=?", (user.user_id,))
            permissions = queryCursor.fetchall()
            return permissions

    @staticmethod
    def getUserPassword(user_name):
        queryCursor.execute("SELECT password FROM users WHERE name=?", (user_name,))
        password = queryCursor.fetchone()
        if password is None:
            print "Failed getting password: user '{}' not found".format(user_name)
	return password[0]

    @staticmethod
    def getAllUserNames():
        names = queryCursor.execute("SELECT name FROM users").fetchall()
        if names is None:
            print "Failed getting usernames: no users found"
        return names

    @staticmethod
    def getPolicies():
        names = queryCursor.execute("SELECT * FROM policies").fetchall()
        return names

    @staticmethod
    def addPermission(user_id, switch_id, permission):
        queryCursor.execute("SELECT perms FROM permissions WHERE user_id=? AND device_id=?", (user_id, switch_id))
        stored_permission = queryCursor.fetchone()
        if stored_permission is None:
            try:
                queryCursor.execute("INSERT INTO permissions (user_id, device_id, perms) VALUES (?,?,?)", (user_id, switch_id, permission))
                dbVar.commit()
                return True
            except:
                #print "Failed adding permission: could not commit to the database"
                return False
        else:
            permission = permission | stored_permission[0]
            try:
                queryCursor.execute("UPDATE permissions SET perms=? WHERE user_id=? AND device_id=?", (permission, user_id, switch_id))
                dbVar.commit()
                return True
            except:
                #print "Failed adding permission: could not commit to the database"
                return False

    @staticmethod
    def removePermission(user_id, switch_id, permission):
        try:
            queryCursor.execute("UPDATE permissions SET perms=? WHERE user_id=? AND device_id=?", (permission, user_id, switch_id))
            dbVar.commit()
            return True
        except:
            #print "Failed removing permission: could not commit to the database"
            return False
