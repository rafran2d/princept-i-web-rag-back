class SaveChatError(Exception):
    pass
    #raised when creating chunk in the database failed

class UpdateTiltleChatError(Exception):
    pass
    #raised when the select chat from the database doesn't return anything

class DeleteChatError(Exception):
    pass