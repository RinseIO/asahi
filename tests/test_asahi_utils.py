import unittest
from mock import patch, MagicMock
from asahi import utils


class TestAsahiUtils(unittest.TestCase):
    def test_asahi_utils_get_elasticsearch(self):
        with patch('django.conf.settings.ELASTICSEARCH_URL', new='http://es:9200'):
            with patch('elasticsearch.Elasticsearch', new=MagicMock(return_value='es')) as mock_es:
                es = utils.get_elasticsearch()
                self.assertEqual(es, 'es')
            mock_es.assert_called_once_with('http://es:9200')
