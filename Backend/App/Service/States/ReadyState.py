from .BaseStatesClasse import DocumentBaseStates

class ReadyState(DocumentBaseStates) :
    def __init__(self,main):
        pass
    async def involve(self,main) :
        pass
    async def fail(self,main) :
        pass
    def retry(self,main) :
        pass
