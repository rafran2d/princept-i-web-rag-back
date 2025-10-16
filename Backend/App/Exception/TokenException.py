class CreateTokenError(Exception):
    pass
#Raised when creating a refreh_token in the db failed

class ReadTokenError(Exception):
    pass
#Raised when reading a refresh_toktn from the db failed

class TokenRevokedError(Exception):
    pass
#Raised when a refresh_token is revoked

class TokenNotFoundError(Exception):
    pass
#Raised when a refresh_token doesn't exist in the database

class RevokeTokenError(Exception):
    pass
#Raised when revoking a token failed