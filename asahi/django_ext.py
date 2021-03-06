import sys, inspect
from django.db.models import signals
from django.conf import settings
from restkit import BasicAuth
from couchdbkit import Server as CouchDBServer
from couchdbkit.exceptions import ResourceNotFound
from couchdbkit.resource import CouchdbResource
from elasticsearch.exceptions import NotFoundError
import utils


class Handler(object):
    def __init__(self, databases, user, password):
        self.databases = databases
        if user and password:
            self.auth = BasicAuth(user, password)
        else:
            self.auth = None

    def sync(self, app):
        app_name = app.__name__.rsplit('.', 1)[0]
        db_url = self.__get_db_url(app_name)
        if db_url is None:
            return

        # get server and db
        server_uri, db_name = db_url.rsplit("/", 1)
        print('sync `%s` in CouchDB' % db_name)
        if self.auth:
            res = CouchdbResource(server_uri, filters=[self.auth])
        else:
            res = CouchdbResource(server_uri)
        server = CouchDBServer(server_uri, resource_instance=res)
        db = server.get_or_create_db(db_name)

        # save _design
        doc_id = '_design/%s' % db_name
        doc = {
            'views': {
                'id': {
                    'map': 'function(doc){emit(doc._id, doc);}'
                }
            },
            '_id': doc_id,
        }
        try:
            old_doc = db.open_doc(doc_id)
            doc['_rev'] = old_doc['_rev']
        except ResourceNotFound:
            pass
        db.save_doc(doc)


    def re_index(self, document_class=None):
        from document import Document
        if document_class is None:
            # re-index all indices
            for app in settings.INSTALLED_APPS:
                if "django" not in app:
                    try:
                        members = inspect.getmembers(sys.modules['%s.models' % app])
                    except:
                        continue
                    for name, cls in members:
                        is_document = False
                        try:
                            if issubclass(cls, Document) and name != 'Document':
                                is_document = True
                        except:
                            pass
                        if is_document:
                            self.re_index(cls)
            return

        es = utils.get_elasticsearch()
        db = document_class.get_db()
        print('re-index `%s` in ElasticSearch' % db.dbname)
        documents = db.view(
            '%s/id' % db.dbname,
            schema=document_class,
            wrapper=None,
            wrap_doc=True,
        ).all()
        try:
            es.indices.delete(db.dbname)
        except NotFoundError:
            pass
        es.indices.create(db.dbname)
        if db.dbname == 'ispo_specials':
            es.indices.put_mapping(
                index=db.dbname,
                doc_type=document_class.__name__,
                body={
                    'properties': {
                        'groups': {'type': 'string', 'index': 'not_analyzed'}
                    }
                }
            )
        for doc in documents:
            try:
                es.index(
                    index=db.dbname,
                    doc_type=document_class.__name__,
                    id=doc._id,
                    body=doc._doc
                )
            except:
                pass

    def __get_db_url(self, app_name):
        for database in self.databases:
            name, url = database
            if name == app_name:
                return url
        return None

def syncdb(app, created_models, **kwargs):
    """ function used by syncdb signal """
    handler = Handler(
        getattr(settings, "COUCHDB_DATABASES", []),
        getattr(settings, "COUCHDB_USER", None),
        getattr(settings, "COUCHDB_PASSWORD", None),
    )

    # sync views of CouchDB
    handler.sync(app)

signals.post_syncdb.connect(syncdb)
