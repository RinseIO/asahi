from couchdbkit.schema import DocumentBase
from query import Query


class Document(DocumentBase):
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