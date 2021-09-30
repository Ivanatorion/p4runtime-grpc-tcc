import EventType

class FlowruleEvent():
    
    def __init__(self, app, switch):
        self.type = EventType.FLOWRULE_EVENT
        self.app = app
        self.switch = switch
