class UserCreateError(Exception):
    pass
#Raised when error has been encountered during the creation user process

class EmailAlreadyUsedError(Exception):
    pass
#Raised when a user try to sign up with an email already linked to another user

class ReadUserError(Exception):
    pass
#Raised when reading user from teh db encounter an error

class EmailStructError(Exception):
    pass
#Raised when tht email is not valid

class UserNotFoundError(Exception):
    pass
#Raised when tht email is not linked to an existing acount

class UserNotFoundError(Exception):
    pass
#Raised when the id doesn't match with any user's id from the db

class DeleteUserError(Exception):
    pass
#Raised when deleting user from teh db encounter an error

class IncorrectPasswordError(Exception):
    pass
#Raised when the mdp is incorrect