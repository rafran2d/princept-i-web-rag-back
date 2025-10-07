class UnsupportedFileTypeError(Exception):
    #raised when the doc is not a pdf or docx
    pass

class DocumentFailedError(Exception):
    #raised when doc status is failed 
    pass

class ChunkingError(Exception):
    #raised when the chunking process bugged
    pass

class SaveChunkError(Exception):
    #raised when  saving chunk to the base failed
    pass

class UpdateDocumentStatusError(Exception):
    #raised when the doc status transformation process failed
    pass

class EmbeddingError(Exception):
    #raised when the embedding process failed
    pass

class SaveEmbeddingError(Exception):
    #raised when saving the embedding to the base failed
    pass

class SaveDocumentError(Exception):
    #raised when saving the document to the base failed
    pass

class AddMetadataError(Exception):
    #raised when Addig metadata to the documetn failed
    pass

