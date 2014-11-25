from django.conf import settings
import elasticsearch


def get_elasticsearch():
    """
    Get the connection for ElasticSearch.
    :return: {Elasticsearch}
    """
    return elasticsearch.Elasticsearch(get_elasticsearch_url())

def get_elasticsearch_url():
    """
    Get Elasticsearch server's url.
    :return: {string}
    """
    return getattr(settings, 'ELASTICSEARCH_URL', 'http://localhost:9200')

def get_index_prefix():
    """

    :return: {string}
    """
    return getattr(settings, 'ASAHI_DB_PREFIX', '')
