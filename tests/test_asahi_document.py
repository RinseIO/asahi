import unittest
from mock import MagicMock, patch
from tests import patcher
from asahi.document import Document


class TestAsahiDocument(unittest.TestCase):
    @patcher(
        patch('asahi.document.Document._db', new_callable=MagicMock(return_value='db')),
    )
    def test_asahi_document_get_db_not_none(self):
        db = Document.get_db()
        self.assertEqual(db, 'db')

    def test_asahi_document_get_db_none(self):
        from asahi import document
        fake_meta = MagicMock()
        fake_meta.app_label = 'app_label'
        Document._meta = fake_meta
        self.patches = [
            patch('asahi.document.get_db', new=MagicMock(return_value='db')),
        ]
        map(lambda x: x.start(), self.patches)
        db = Document.get_db()
        document.get_db.assert_called_with('app_label')
        self.assertEqual(db, 'db')
        map(lambda x: x.stop, self.patches)

    @patcher(
        patch('asahi.document.DocumentBase.get', new=MagicMock(return_value='document')),
    )
    def test_asahi_document_get_by_id(self):
        from asahi.document import DocumentBase
        document = Document.get('id')
        DocumentBase.get.assert_called_with('id', None, None, True)
        self.assertEqual(document, 'document')

    def test_asahi_document_get_by_ids(self):
        self.fake_db = MagicMock()
        self.fake_db().dbname = 'dbname'
        self.fake_db().view().all.return_value = 'all'
        self.patches = [
            patch('asahi.document.Document.get_db', new=self.fake_db),
        ]
        map(lambda x: x.start(), self.patches)
        documents = Document.get(['id'])
        Document.get_db.assert_called()
        Document.get_db().view.assert_called_with(
            'dbname/id',
            keys=['id'],
            schema=Document)
        Document.get_db().view().all.assert_called()
        self.assertEqual(documents, 'all')
        map(lambda x: x.stop(), self.patches)

    def test_asahi_document_where(self):
        self.fake_query = MagicMock()
        self.fake_query().intersect.return_value = 'query'
        self.patches = [
            patch('asahi.document.Query', new=self.fake_query),
        ]
        map(lambda x: x.start(), self.patches)
        query = Document.where('email', equal='kelp@rinse.io')
        self.fake_query.assert_called_with(Document)
        self.fake_query(Document).intersect.assert_called_with('email', equal='kelp@rinse.io')
        self.assertEqual(query, 'query')
        map(lambda x: x.stop(), self.patches)

    def test_asahi_document_all(self):
        self.fake_query = MagicMock(return_value='query')
        self.patches = [
            patch('asahi.document.Query', new=self.fake_query),
        ]
        map(lambda x: x.start(), self.patches)
        query = Document.all()
        self.fake_query.assert_called_once_with(Document)
        self.assertEqual(query, 'query')
        map(lambda x: x.stop(), self.patches)
