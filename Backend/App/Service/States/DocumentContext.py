from .PendingState import  PendingState

class DocumentContext():

    def __init__(self,id):
        self.id = id
        self.state =  PendingState(self)
    
    def involve(self):
        self.state.involve(self)

    def fail (self):
        self.state.fail(self)

    def retry(self):
        self.prevstate.retry(self)