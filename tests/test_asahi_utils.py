import unittest
from mock import patch, MagicMock
from tests import patcher
from asahi import utils


class TestAsahiUtils(unittest.TestCase):
    @patcher(
        patch('asahi.utils.get_elasticsearch_url', new=MagicMock(return_value='http://localhost:9200')),
        patch('elasticsearch.Elasticsearch', new=MagicMock(return_value='es')),
    )
    def test_asahi_utils_get_elasticsearch(self):
        from elasticsearch import Elasticsearch
        es = utils.get_elasticsearch()
        Elasticsearch.assert_called_with('localhost', port=9200)
        self.assertEqual(es, 'es')

    @patcher(
        patch('django.conf.settings.ELASTICSEARCH_URL', new_callable=MagicMock(return_value='es')),
    )
    def test_asahi_utils_get_elasticsearch_url(self):
        url = utils.get_elasticsearch_url()
        self.assertEqual(url, 'es')
