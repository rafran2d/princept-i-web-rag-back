class ReadChunkError(Exception) :
    pass
# raised when Reading chunk from the db encounter an error

class ChunkStepError(Exception) :
    pass
# raise when the chunk_step process encoutner an error