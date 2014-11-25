from query import Query
import utils
from .properties import Property, StringProperty, LongProperty
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
        cls._index_name = '%s%s' % (utils.get_index_prefix(), cls.__name__.lower())
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
                self._document[property_name] = kwargs[property_name]
            else:
                self._document[property_name] = property.default


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
                index=cls._index_name,
                doc_type=cls.__name__,
                body={
                    'ids': ids
                },
            )
            return [cls(_id=x['_id'], _version=x['_version'], **x['_source']) for x in result['docs'] if x['found']]

        # fetch the document
        try:
            result = es.get(
                index=cls._index_name,
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
        document = self._document.copy()
        del document['_id']
        del document['_version']
        result = es.index(
            index=self._index_name,
            doc_type=self.__class__.__name__,
            id=self._id,
            version=self._version,
            body=document
        )
        self._id = result.get('_id')
        self._version = result.get('_version')
        if is_synchronized:
            es.indices.flush()

    def delete(self, is_synchronized=False):
        """
        Delete the document.
        """
        if not self._id:
            return None

        es = utils.get_elasticsearch()
        es.delete(
            index=self._index_name,
            doc_type=self.__class__.__name__,
            id=self._id,
        )
        if is_synchronized:
            es.indices.flush()
