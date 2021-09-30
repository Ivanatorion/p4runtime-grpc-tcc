
class SwitchTableObject():

    def __init__(self, switch_id, table_id, table_name, match_type, base_address):
        self.switch_id = switch_id
        self.table_id = table_id
        self.table_name = table_name
        self.match_type = match_type
        self.base_address = base_address
        self.match_fields = []
