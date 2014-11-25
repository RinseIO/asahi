from elasticsearch import exceptions

class BadValueError(Exception):
    """
    exception raised when a value can't be validated or is required
    """
ConflictError = exceptions.ConflictError
NotFoundError = exceptions.NotFoundError
