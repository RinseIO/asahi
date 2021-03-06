from datetime import datetime
from . import utils
from .query import Query
from .properties import Property, StringProperty, IntegerProperty, DateTimeProperty, ListProxy
from .exceptions import NotFoundError
from .deep_query import update_reference_properties


class Document(object):
    """
    :attribute _index: {string} You can set index of this Document.
    :attribute _id: {string}
    :attribute _version: {int}
    :attribute _document: {dict} {'property_name': (value)}
    :attribute _reference_document: {dict} {'property_name': {Document}}
    :attribute _properties: {dict} {'property_name': {Property}}
    :attribute _es: {Elasticsearch}
    :attribute _index_name: {string}
    """
    _id = StringProperty()
    _version = IntegerProperty()
    _es = utils.get_elasticsearch()

    def __new__(cls, *args, **kwargs):
        cls._properties = cls.__get_properties()
        cls._properties_in = cls  # memo cls._properties from which class
        return object.__new__(cls, *args)

    def __init__(self, **kwargs):
        super(Document, self).__init__()
        self._document = {}
        self._reference_document = {}
        for property_name, property in self._properties.items():
            if property_name in kwargs.keys():
                setattr(self, property_name, kwargs[property_name])
            else:
                setattr(self, property_name, property.default)

    @classmethod
    def __get_properties(cls):
        """
        Get properties of this class.
        :return: {dict} {'property_name': {Property}}
        """
        properties = {}
        for attribute_name in dir(cls):
            if attribute_name.startswith('__'):
                continue
            attribute = getattr(cls, attribute_name)
            if isinstance(attribute, Property) or isinstance(attribute, ListProxy):
                properties[attribute_name] = attribute
                attribute.__property_config__(cls, attribute_name)
        return properties

    @classmethod
    def get_properties(cls):
        """
        Some time the class didn't call initial function but need get properties list.
        :return: {dict} {'property_name': {Property}}
        """
        if not hasattr(cls, '_properties_in') or not cls is cls._properties_in\
                or not hasattr(cls, '_properties'):
            cls._properties = cls.__get_properties()
            cls._properties_in = cls
        return cls._properties

    @classmethod
    def get_index_name(cls):
        if not hasattr(cls, '_index_name') or not cls._index_name:
            if hasattr(cls, '_index') and cls._index:
                cls._index_name = '%s%s' % (utils.get_index_prefix(), cls._index)
            else:
                cls._index_name = '%s%s' % (utils.get_index_prefix(), cls.__name__.lower())
        return cls._index_name

    @classmethod
    def get(cls, ids, fetch_reference=True):
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
            if not len(ids):
                return []

            def __get():
                return es.mget(
                    index=cls.get_index_name(),
                    doc_type=cls.__name__,
                    body={
                        'ids': list([x for x in set(ids) if not x is None])
                    },
                )

            try:
                response = __get()
            except NotFoundError as e:
                if 'IndexMissingException' in str(e):  # try to create index
                    es.indices.create(index=cls.get_index_name())
                    response = __get()
                else:
                    raise e
            result_table = {x['_id']: x for x in response['docs'] if x['found']}
            result = []
            for document_id in ids:
                document = result_table.get(document_id)
                if document:
                    result.append(cls(_id=document['_id'], _version=document['_version'], **document['_source']))
            if fetch_reference:
                update_reference_properties(result)
            return result

        # fetch the document
        try:
            def __get():
                return es.get(
                    index=cls.get_index_name(),
                    doc_type=cls.__name__,
                    id=ids,
                )

            try:
                response = __get()
            except NotFoundError as e:
                if 'IndexMissingException' in str(e):  # try to create index
                    es.indices.create(index=cls.get_index_name())
                    response = __get()
                else:
                    raise e
            result = cls(_id=response['_id'], _version=response['_version'], **response['_source'])
            if fetch_reference:
                update_reference_properties([result])
            return result
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
            unlike,
            contains,
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

    @classmethod
    def refresh(cls):
        """
        Explicitly refresh the index, making all operations performed
        since the last refresh available for search.
        `<http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/indices-refresh.html>`_
        """
        cls._es.indices.refresh(index=cls.get_index_name())

    def save(self, synchronized=False):
        """
        Save the document.
        """
        if self._version is None:
            self._version = 0
        for property_name, property in self._properties.items():
            if isinstance(property, DateTimeProperty) and property.auto_now and not getattr(self, property_name):
                setattr(self, property_name, datetime.utcnow())
        document = self._document.copy()
        del document['_id']
        del document['_version']
        result = self._es.index(
            index=self.get_index_name(),
            doc_type=self.__class__.__name__,
            id=self._id,
            version=self._version,
            body=document
        )
        self._id = result.get('_id')
        self._version = result.get('_version')
        if synchronized:
            self._es.indices.refresh(index=self.get_index_name())
        return self

    def delete(self, synchronized=False):
        """
        Delete the document.
        """
        if not self._id:
            return None

        self._es.delete(
            index=self.get_index_name(),
            doc_type=self.__class__.__name__,
            id=self._id,
        )
        if synchronized:
            self._es.indices.refresh(index=self.get_index_name())
        return self
