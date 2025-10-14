from App.Service.Document_service import set_document_failed,set_charged_document
from .BaseStatesClasse import DocumentBaseStates
from .ChunkedState import ChunkedState
from .FailedState import FailedState

class PendingState(DocumentBaseStates) :
    def __init__(self,main):
        self.main = main

    async def involve(self,main) :
        main.prevstate = self
        main.state =  ChunkedState(main)
        await set_charged_document(main.id)

    async def fail(self,main) :
        main.prevstate = self
        main.state = FailedState(main)
        await set_document_failed(main.id)

    def retry(self,main) :
        pass

