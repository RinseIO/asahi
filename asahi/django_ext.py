from django.db.models import signals
from django.conf import settings
from restkit import BasicAuth
from couchdbkit import Server as CouchDBServer
from couchdbkit.exceptions import ResourceNotFound
from couchdbkit.resource import CouchdbResource


class Handler(object):
    def __init__(self, databases, user, password):
        self.databases = databases
        if user and password:
            self.auth = BasicAuth(user, password)
        else:
            self.auth = None

    def sync(self, app):
        app_name = app.__name__.rsplit('.', 1)[0]
        db_url = None
        for database in self.databases:
            name, url = database
            if name == app_name:
                db_url = url
                break
        if db_url is None:
            return
        print('sync `%s` in CouchDB' % app_name)

        # get server and db
        server_uri, db_name = db_url.rsplit("/", 1)
        if self.auth:
            res = CouchdbResource(server_uri, filters=[self.auth])
        else:
            res = CouchdbResource(server_uri)
        server = CouchDBServer(server_uri, resource_instance=res)
        db = server.get_or_create_db(db_name)

        # save _design
        doc_id = '_design/%s' % app_name
        doc = {
            'views': {
                'id': {
                    'map': u'function(doc){emit(doc._id, doc);}'
                }
            },
            '_id': doc_id,
        }
        try:
            doc = db.open_doc(doc_id)
            doc['_rev'] = doc['_rev']
        except ResourceNotFound:
            pass
        db.save_doc(doc, force_update=True)

def syncdb(app, created_models, **kwargs):
    """ function used by syncdb signal """
    handler = Handler(
        getattr(settings, "COUCHDB_DATABASES", []),
        getattr(settings, "COUCHDB_USER", None),
        getattr(settings, "COUCHDB_PASSWORD", None),
    )
    handler.sync(app)

signals.post_syncdb.connect(syncdb)
