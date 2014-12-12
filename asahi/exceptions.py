from elasticsearch import exceptions

class BadValueError(Exception):
    """
    exception raised when a value can't be validated or is required
    """
    pass
class PropertyNotExist(Exception):
    """
    exception raised when a member not match any properties
    """
    pass
ConflictError = exceptions.ConflictError
NotFoundError = exceptions.NotFoundError
ConnectionError = exceptions.ConnectionError
