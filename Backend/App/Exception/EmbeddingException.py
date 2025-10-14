class ReadEmbeddingError(Exception) :
    pass
#Raised when reading embedding from the db encountered an error

class EmbeddingStepError(Exception) :
    pass
#Raised when an Error is encountered during the Embedding process