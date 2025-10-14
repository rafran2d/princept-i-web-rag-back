from App.Service.Document_service import (
    set_document_failed,
    set_ready_document,
    read_document_id
)
from App.Controller.EmbeddingController import batch_embedding_process
from .BaseStatesClasse import DocumentBaseStates
from .ReadyState import ReadyState
from .FailedState import FailedState

class ChunkedState(DocumentBaseStates) :
    def __init__(self,main) :
        self.main = main

    async def involve(self,main) :
        main.prevstate = self
        main.state =  ReadyState(main)
        await set_ready_document(main.id)

    async def fail(self,main) :
        main.prevstate = self
        main.state = FailedState(main)
        await set_document_failed(main)

    async def retry(self,main) :
        try:
            doc = await read_document_id(main.id)
            await batch_embedding_process(doc.chunks)
        except Exception as e :
            raise e