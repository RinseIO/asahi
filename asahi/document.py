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
    def where(cls, member, **kwargs):
        """
        The where query.
        :param member: The member's name of the document.
        :param kwargs: [
            unequal,
            equal,
            less,
            less_equal,
            greater,
            greater_equal,
            like,
        ]
        """
        query = Query(cls)
        return query.intersect(member, **kwargs)

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
