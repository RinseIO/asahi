from couchdbkit.ext import django as couchdb_ext_django
from couchdbkit.exceptions import ResourceNotFound
del couchdb_ext_django.syncdb # delete couchdbkit.syncdb
import django_ext # added asahi.syncdb for django
from couchdbkit.schema import DocumentBase
from couchdbkit.ext.django.schema import DocumentMeta
from couchdbkit.ext.django.loading import get_db
from query import Query
import utils
from .properties import Property, StringProperty, LongProperty


class Document(object):
    """
    :attribute _document: {dict} {'property_name': (value)}
    :attribute _properties: {dict} {'property_name': {Property}}
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
                self._document[property_name] = kwargs[property_name]
            else:
                self._document[property_name] = property.default



    # @classmethod
    # def get(cls, ids, rev=None, db=None, dynamic_properties=True):
    #     """
    #     Get documents by ids.
    #     :param ids: {list or string} The documents' id.
    #     :return: {list or Document}
    #     """
    #     if ids is None:
    #         return None
    #     if isinstance(ids, list):
    #         if db is None:
    #             db = cls.get_db()
    #         return db.view(
    #             '%s/id' % db.dbname,
    #             keys=ids,
    #             schema=cls
    #         ).all()
    #     else:
    #         try:
    #             return super(Document, cls).get(ids, rev, db, dynamic_properties)
    #         except ResourceNotFound:
    #             return None

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
            index='%s%s' % (utils.get_index_prefix(), self.__class__.__name__.lower()),
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
        es = utils.get_elasticsearch()
        es.delete(
            index='%s%s' % (utils.get_index_prefix(), self.__class__.__name__.lower()),
            doc_type=self.__class__.__name__,
            id=self._id,
        )
        if is_synchronized:
            es.indices.flush()
