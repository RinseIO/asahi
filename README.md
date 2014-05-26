#asahi

A database library for CouchDB and ElasticSearch.



##Installation
>```bash
$ git submodule add git@github.com:RinseIO/asahi.git
$ git submodule add https://github.com/RinseIO/couchdbkit.git
$ pip install elasticsearch
```



##Document
>The [asahi document](https://github.com/RinseIO/asahi/blob/master/asahi/document.py#L11) is base on couchdbkit.ext.django.schema.DocumentBase.
```python
from asahi import db
class SampleModel(db.Document):
    name = db.StringProperty()
    email = db.StringProperty(required=True)
    is_vip = db.BooleanProperty(default=False)
    quota = db.FloatProperty(default=0.0)
    created_at = db.DateTimeProperty(auto_now_add=True)
```

**Methods**
>```python
def get(cls, ids, rev=None, db=None, dynamic_properties=True):
    """
    Get documents by ids.
    :param ids: {list or string} The documents' id.
    :return: {list or Document}
    """
# example:
#    Get the document by the id.
#    The result document is SampleModel's instance.
document = SampleModel.get('8ee4891d79182647b80c53e0a21f4a6d')
#    Get the documents by ids.
#    The result documents is the list. There are SampleModels' instance in the list.
documents = SampleModel.get([
        '8ee4891d79182647b80c53e0a21f4a6d',
        '7ccecde23f7bf67b2b6586f9917c259c',
    ])
```
```python
def where(cls, *args, **kwargs):
    """
    Intersect the query.
    :param args:
        The member's name of the document or
            the sub queries' lambda function.
    :param kwargs: [
        unequal,
        equal,
        less,
        less_equal,
        greater,
        greater_equal,
        like,
        among,
    ]
    :return: {asahi.query.Query}
    """
```
```python
def all(cls):
    """
    The query for all documents.
    :return: {asahi.query.Query}
    """
```
```python
def save(self, **params):
    """
    Save the document.
    """
```
```python
def delete(self):
    """
    Delete the document.
    """
```



##Query
>The asahi query.

**Methods**
>```python
def where(self, *args, **kwargs):
    """
    Intersect the query.
    :param args:
        The member's name of the document or
            the sub queries' lambda function.
    :param kwargs: [
        unequal,
        equal,
        less,
        less_equal,
        greater,
        greater_equal,
        like,
        among,
    ]
    :return: {asahi.query.Query}
    """
```
```python
def order_by(self, member, descending=False):
    """
    Append the order query.
    :param member: {string} The property name of the document.
    :param descending: {bool} Is sorted by descending.
    :return: {asahi.query.Query}
    """
```
```python
def fetch(self, limit=1000, skip=0):
    """
    Fetch documents by the query.
    :param limit: {int} The size of the pagination. (The limit of the result items.)
    :param skip: {int} The offset of the pagination. (Skip x items.)
    :returns: {list}, {int}
        The documents.
        The total items.
    """
```
```python
def first(self):
    """
    Fetch the first document.
    :return: {asahi.document.Document or None}
    """
```
```python
def count(self):
    """
    Count documents by the query.
    :return: {int}
    """
```



##Examples
>```sql
select * from "ExampleModel" where "name" = "asahi"
```
```python
models, total = ExampleModel.where('name', equal='asahi').fetch()
```

---
>```sql
select * from "ExampleModel" where "name" = "asahi" and "email" = "asahi@rinse.io"
```
```python
models, total = ExampleModel.where('name', equal='asahi')\
        .where('email', equal='asahi@rinse.io')\
        .fetch()
```

---
>```sql
select * from "ExampleModel" where "name" like "%asahi%" or "email" like "%asahi%"
```
```python
models, total = ExampleModel.where(lambda x:
    x.where('name', like='asahi')
    .union('email', like='asahi')
).fetch()
```

---
>```sql
select * from "ExampleModel" where "category" = 1 or "category" = 3
        order by "created_at" limit 20 offset 20
```
```python
models, total = ExampleModel.where('category', among=[1, 3])\
        .order_by('created_at').fetch(20, 20)
```

---
>Fetch the first item.
```sql
select * from "ExampleModel" where "age" >= 10
         order by "created_at" desc limit 1
```
```python
model = ExampleModel.where('age', greater_equal=10)\
        .order_by('created_at', descending=True).first()
```

---
>Count items.
```sql
select count(*) from "ExampleModel" where "age" < 10
```
```python
count = ExampleModel.where('age', less=10).count()
```



##Properties
>https://github.com/RinseIO/asahi/blob/master/asahi/properties.py
+ Property
+ StringProperty
+ IntegerProperty
+ DecimalProperty
+ BooleanProperty
+ FloatProperty
+ DateTimeProperty
+ DateProperty
+ TimeProperty
+ SchemaProperty
+ SchemaListProperty
+ ListProperty
+ DictProperty
+ StringDictProperty
+ StringListProperty
+ SchemaDictProperty
+ SetProperty



##Requirement
>```bash
$ git submodule update --init
$ pip install -r pip_requirements.txt
```



##unit-test
>```bash
$ python test.py
```



##django manage.py
###sync CouchDB's views
>```bash
$ python manage.py syncdb
```

###re-index ElasticSearch
>```bash
delete ElasticSearch all indices than add from CouchDB
$ python manage.py reindex
```
```python
# create a file `reindex.py` at your app
# {your_app}/management/commands/reindex.py
from django.core.management.base import BaseCommand
from django.conf import settings
from asahi.django_ext import Handler
class Command(BaseCommand):
    def handle(self, *args, **options):
        handler = Handler(
            getattr(settings, "COUCHDB_DATABASES", []),
            getattr(settings, "COUCHDB_USER", None),
            getattr(settings, "COUCHDB_PASSWORD", None),
        )
        handler.re_index()
```



##References
>+ [elasticsearch-queries](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-queries.html)
