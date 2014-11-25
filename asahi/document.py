from datetime import datetime
from query import Query
import utils
from .properties import Property, StringProperty, LongProperty, DateTimeProperty
from .exceptions import NotFoundError


class Document(object):
    """
    :attribute _id: {string}
    :attribute _version: {long}
    :attribute _document: {dict} {'property_name': (value)}
    :attribute _properties: {dict} {'property_name': {Property}}
    :attribute _index_name: {string}
    """
    _id = StringProperty()
    _version = LongProperty()

    def __new__(cls, *args, **kwargs):
        cls._properties = {}
        for attribute_name in dir(cls):
            if attribute_name.startswith('__'):
                continue
            attribute = getattr(cls, attribute_name)
            if isinstance(attribute, Property):
                cls._properties[attribute_name] = attribute
                attribute.__property_config__(cls, attribute_name)
        return object.__new__(cls, *args)

    def __init__(self, **kwargs):
        super(Document, self).__init__()
        self._document = {}
        argument_keys = kwargs.keys()
        for property_name, property in self._properties.items():
            if property_name in argument_keys:
                setattr(self, property_name, kwargs[property_name])
            else:
                setattr(self, property_name, property.default)

    @classmethod
    def get_index_name(cls):
        if not hasattr(cls, '_index_name') or not cls._index_name:
            cls._index_name = '%s%s' % (utils.get_index_prefix(), cls.__name__.lower())
        return cls._index_name

    @classmethod
    def get(cls, ids):
        """
        Get documents by ids.
        :param ids: {list or string} The documents' id.
        :return: {list or Document}
        """
        if ids is None:
            return None
        es = utils.get_elasticsearch()
        if isinstance(ids, list):
            # fetch documents
            result = es.mget(
                index=cls.get_index_name(),
                doc_type=cls.__name__,
                body={
                    'ids': ids
                },
            )
            return [cls(_id=x['_id'], _version=x['_version'], **x['_source']) for x in result['docs'] if x['found']]

        # fetch the document
        try:
            result = es.get(
                index=cls.get_index_name(),
                doc_type=cls.__name__,
                id=ids,
            )
            return cls(_id=result['_id'], _version=result['_version'], **result['_source'])
        except NotFoundError:
            return None

    @classmethod
    def where(cls, *args, **kwargs):
        """
        Intersect the query.
        :param args:
            The member's name of the document or
                the sub queries' lambda function.
        :param kwargs: [
            unequal,
            equal,
            less,
            less_equal,
            greater,
            greater_equal,
            like,
            among,
        ]
        :return: {asahi.query.Query}
        """
        query = Query(cls)
        return query.intersect(*args, **kwargs)

    @classmethod
    def all(cls):
        """
        The query for all documents.
        :return: {asahi.query.Query}
        """
        return Query(cls)

    def save(self, is_synchronized=False):
        """
        Save the document.
        """
        es = utils.get_elasticsearch()
        if self._version is None:
            self._version = 0L
        for property_name, property in self._properties.items():
            if isinstance(property, DateTimeProperty) and property.is_auto_now and not getattr(self, property_name):
                setattr(self, property_name, datetime.utcnow())
        document = self._document.copy()
        del document['_id']
        del document['_version']
        result = es.index(
            index=self.get_index_name(),
            doc_type=self.__class__.__name__,
            id=self._id,
            version=self._version,
            body=document
        )
        self._id = result.get('_id')
        self._version = result.get('_version')
        if is_synchronized:
            es.indices.flush(index=self.get_index_name())

    def delete(self, is_synchronized=False):
        """
        Delete the document.
        """
        if not self._id:
            return None

        es = utils.get_elasticsearch()
        es.delete(
            index=self.get_index_name(),
            doc_type=self.__class__.__name__,
            id=self._id,
        )
        if is_synchronized:
            es.indices.flush(index=self.get_index_name())
