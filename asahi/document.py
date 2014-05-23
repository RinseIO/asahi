from couchdbkit.ext import django as couchdb_ext_django
del couchdb_ext_django.syncdb # delete couchdbkit.syncdb
import django_ext # added asahi.syncdb for django
from couchdbkit.schema import DocumentBase
from couchdbkit.ext.django.schema import DocumentMeta
from couchdbkit.ext.django.loading import get_db
from query import Query
import utils


class Document(DocumentBase):
    __metaclass__ = DocumentMeta

    @classmethod
    def get_db(cls):
        db = getattr(cls, '_db', None)
        if db is None:
            app_label = getattr(cls._meta, "app_label")
            db = get_db(app_label)
            cls._db = db
        return db

    @classmethod
    def get(cls, ids, rev=None, db=None, dynamic_properties=True):
        """
        Get documents by ids.
        :param ids: {list or string} The documents' id.
        :return: {list or Document}
        """
        if isinstance(ids, list):
            if db is None:
                db = cls.get_db()
            return db.view(
                '%s/id' % db.dbname,
                keys=ids,
                schema=cls
            ).all()
        else:
            return super(Document, cls).get(ids, rev, db, dynamic_properties)

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

    def save(self, **params):
        """
        Save the document.
        """
        super(Document, self).save(**params)
        es = utils.get_elasticsearch()
        es.index(
            index=self.get_db().dbname,
            doc_type=self.__class__.__name__,
            id=self._id,
            body=self._doc
        )
        es.indices.flush()

    def delete(self):
        """
        Delete the document.
        """
        super(Document, self).delete()
        es = utils.get_elasticsearch()
        es.delete(
            index=self.get_db().dbname,
            doc_type=self.__class__.__name__,
            id=self._id,
        )
        es.indices.flush()
