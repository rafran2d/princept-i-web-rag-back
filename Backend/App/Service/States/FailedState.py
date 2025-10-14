from .BaseStatesClasse import DocumentBaseStates

class FailedState(DocumentBaseStates) :
    def __init__(self,main):
        pass
    async def retry(self,main) :
        pass
    async def involve(self,main) :
        pass
    def fail(self,main) :
        pass