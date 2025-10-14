from abc import ABC,abstractclassmethod

class DocumentBaseStates(ABC):
    @abstractclassmethod
    async def involve(self,main):
        pass

    @abstractclassmethod
    async def fail(self,main):
        pass

    @abstractclassmethod
    def retry(self,main):
        pass