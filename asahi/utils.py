from urlparse import urlparse
from django.conf import settings
import elasticsearch


def get_elasticsearch():
    """
    Get the connection for ElasticSearch.
    :return: {Elasticsearch}
    """
    url = urlparse(get_elasticsearch_url())
    return elasticsearch.Elasticsearch(url.hostname, port=url.port)

def get_elasticsearch_url():
    """
    Get Elasticsearch server's url.
    :return: {string}
    """
    return getattr(settings, 'ELASTICSEARCH_URL', 'http://localhost:9200')
