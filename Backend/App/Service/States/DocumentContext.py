from .PendingState import  PendingState

class DocumentContext():

    def __init__(self,id):
        self.id = id
        self.state =  PendingState(self)

    async def involve(self):
        await self.state.involve(self)

    async def fail (self):
        await self.state.fail(self)

    async def retry(self):
        await self.prevstate.retry(self)