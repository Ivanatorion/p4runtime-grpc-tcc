
class SwitchTableActionObject():

    def __init__(self, switch_id, table_id, action_id, action_name):
        self.switch_id = switch_id
        self.table_id = table_id
        self.action_id = action_id
        self.action_name = action_name
        self.action_fields = []
