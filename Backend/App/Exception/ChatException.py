class SaveChatError(Exception):
    pass
    #raised when creating chunk in the database failed

class UpdateTiltleChatError(Exception):
    pass
    #raised when the select chat from the database doesn't return anything

class DeleteChatError(Exception):
    pass
    #raised when deleting chat encounter an error 

class CreateTitleError(Exception):
    pass
    #raise when the creating title chat process encounter an error

class ReadChatError(Exception):
    pass
    #raise when reading chat process encounter an error

class IncrementError(Exception):
    pass

class UnvailableChatError(Exception):
    pass
#The chat is not available 
