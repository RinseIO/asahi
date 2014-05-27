import unittest
from mock import MagicMock
from asahi.query import QueryOperation, QueryCell, Query
from asahi.document import Document


class TestAsahiQueryOperation(unittest.TestCase):
    def test_asahi_query_operation(self):
        self.assertEqual(QueryOperation.normal_operation_mask, 0x3F)
        self.assertEqual(QueryOperation.unequal, 0x000)
        self.assertEqual(QueryOperation.equal, 0x001)
        self.assertEqual(QueryOperation.less, 0x002)
        self.assertEqual(QueryOperation.less_equal, 0x003)
        self.assertEqual(QueryOperation.greater, 0x004)
        self.assertEqual(QueryOperation.greater_equal, 0x005)
        self.assertEqual(QueryOperation.like, 0x010)
        self.assertEqual(QueryOperation.among, 0x020)

        self.assertEqual(QueryOperation.intersection, 0x040)
        self.assertEqual(QueryOperation.union, 0x080)
        self.assertEqual(QueryOperation.all, 0x100)
        self.assertEqual(QueryOperation.order_asc, 0x200)
        self.assertEqual(QueryOperation.order_desc, 0x400)


class TestAsahiQueryCell(unittest.TestCase):
    def test_asahi_query_cell_only_operation(self):
        query = QueryCell(QueryOperation.all)
        self.assertIsNone(query.member)
        self.assertEqual(query.operation, QueryOperation.all)
        self.assertIsNone(query.value)
        self.assertIsNone(query.sub_queries)

    def test_asahi_query_cell(self):
        query = QueryCell(
            QueryOperation.equal,
            'member',
            'value',
            sub_queries=[]
        )
        self.assertEqual(query.member, 'member')
        self.assertEqual(query.operation, QueryOperation.equal)
        self.assertEqual(query.value, 'value')
        self.assertListEqual(query.sub_queries, [])


class TestAsahiQuery(unittest.TestCase):
    def test_asahi_query(self):
        query = Query('document')
        self.assertEqual(query.document, 'document')
        self.assertEqual(len(query.items), 1)
        self.assertEqual(query.items[0].operation, QueryOperation.all)

    def test_asahi_query_where(self):
        query = Query(Document)
        query.intersect = MagicMock()
        query.where('email', equal='kelp@rinse.io')
        query.intersect.assert_called_with('email', equal='kelp@rinse.io')
