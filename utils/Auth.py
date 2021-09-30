from model.AuthDAO import *
from model.SwitchConfDAO import *
from config.PermEnum import *

# Database dict (user_id, switch_id) -> Permission
# Used to avoid multiple queries to the database in critical sections.
dbMemory = {}

class Auth():

    @staticmethod
    def loadDbMemory():
        AuthDAO.loadDbMemory(dbMemory)

    @staticmethod
    def authenticate(user_name, password):
        stored_password = AuthDAO.getUserPassword(user_name)
        if stored_password is not None and stored_password == password:
            return True
        else:
            return False

    @staticmethod
    def addUser(user_name, password):
        return AuthDAO.addUser(user_name, password)

    @staticmethod
    def addPol(needs, receives, response, message):
        return AuthDAO.addPol(needs, receives, response, message)

    @staticmethod
    def getUserByName(user_name):
        return AuthDAO.getUserByName(user_name)

    @staticmethod
    def getUserPermissions(user_name):
        return AuthDAO.getUserPermissions(user_name)

    @staticmethod
    def getAllUserNames():
        return AuthDAO.getAllUserNames()

    @staticmethod
    def getPolicies():
        return AuthDAO.getPolicies()

    @staticmethod
    def getUserLabels(user_name):
        labels = set()
        user = AuthDAO.getUserByName(user_name)

        for switch_id in SwitchConfDAO.getAllSwitchIDs():

            uVifcPerms = 0

            user_perms = "{:026b}".format(dbMemory[(user.user_id, switch_id[0])])
            packet_perms = int(user_perms[6:9], 2)
            flowrule_perms = int(user_perms[12:15], 2)
            config_perms = int(user_perms[23:26], 2)
            device_perms = int(user_perms[17:23], 2)

            if packet_perms != 0:
                labels.add((VIFC_PACKET, switch_id[0]))
                uVifcPerms = uVifcPerms | VIFC_PACKET
            if flowrule_perms != 0:
                labels.add((VIFC_FLOWRULE, switch_id[0]))
                uVifcPerms = uVifcPerms | VIFC_FLOWRULE
            if config_perms != 0:
                labels.add((VIFC_CONFIG, switch_id[0]))
                uVifcPerms = uVifcPerms | VIFC_CONFIG
            if device_perms != 0:
                labels.add((VIFC_DEVICE, switch_id[0]))
                uVifcPerms = uVifcPerms | VIFC_DEVICE

        return labels

    # Username and switch name were kept here because it's easier to add permissions with them.
    # The database accesses to retrieve both ids were moved here because we need them to manipulate
    # the dictionary.
    @staticmethod
    def addPermission(user_name, switch_name, permission):

        # Get user id from the database.
        user = AuthDAO.getUserByName(user_name)
        if user is False:
            print "Failed adding permission: user '{}' was not found".format(user_name)
            return False

        # Get switch id from the database.
        switch = SwitchConfDAO.getSwitchByName(switch_name)
        if switch is False:
            print "Failed adding permission: switch '{}' was not found".format(switch_name)
            return False

        # Add switch permission for user.
        if AuthDAO.addPermission(user.user_id, switch.switch_id, permission) is True:
            try:
                current_permission = dbMemory[(user.user_id, switch.switch_id)]
                dbMemory[(user.user_id, switch.switch_id)] = current_permission | permission
            except KeyError:
                dbMemory[(user.user_id, switch.switch_id)] = permission
            return True
        else:
            return False

    # Same here because it's easier.
    @staticmethod
    def removePermission(user_name, switch_name, permission):

        # Get user id from the database.
        user = AuthDAO.getUserByName(user_name)
        if user is False:
            print "Failed removing permission: user '{}' was not found".format(user_name)
            return False

        # Get switch id from the database.
        switch = SwitchConfDAO.getSwitchByName(switch_name)
        if switch is False:
            print "Failed removing permission: switch '{}' was not found".format(switch_name)
            return False

        # Get the stored permission from the in-memory database.
        try:
            stored_permission = dbMemory[(user.user_id, switch.switch_id)]
        except KeyError:
            print "Failed removing in-memory permission: key does not exist"
            return False

        # Remove the switch permission from the user.
        updated_permission = stored_permission & ~permission
        if AuthDAO.removePermission(user.user_id, switch.switch_id, updated_permission) is True:
            dbMemory[(user.user_id, switch.switch_id)] = updated_permission
            return True
        else:
            return False

    @staticmethod
    def hasPermissionForSwitch(user_id, switch_id, permission):
        try:
            stored_permission = dbMemory[(user_id, switch_id)]
            return (permission & stored_permission) == permission
        except KeyError:
            return False
