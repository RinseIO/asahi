#asahi ![circle-ci](https://circleci.com/gh/RinseIO/asahi.png?circle-token=31b839a690302dd8cbf4c7eee52f63b82ea53cd4)

A database library for ElasticSearch.



##Installation
>```bash
$ git submodule add git@github.com:RinseIO/asahi.git
$ git submodule add https://github.com/RinseIO/elasticsearch-py.git
```



##Document
>
```python
# example:
from asahi import db
# define your data model
class SampleModel(db.Document):
    _index = 'samples'  # You can set index name by this attribute.
    name = db.StringProperty()
    email = db.StringProperty(required=True)
    is_vip = db.BooleanProperty(default=False)
    quota = db.FloatProperty(default=0.0)
    created_at = db.DateTimeProperty(auto_now=True)
```

**Properties**
>```python
_id: {string}
_version: {int}
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
    document = SampleModel.get('byMQ-ULRSJ291RG_eEwSfQ')
#    Get the documents by ids.
#    The result documents is the list. There are SampleModels' instance in the list.
    documents = SampleModel.get([
        'byMQ-ULRSJ291RG_eEwSfQ',
        'byMQ-ULRSJ291RG_eEwSfc',
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
        unlike,
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
def refresh(cls):
    """
    Explicitly refresh the index, making all operations performed
    """
```
```python
def save(self, synchronized=False):
    """
    Save the document.
    """
```
```python
def delete(self, synchronized=False):
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
        unlike,
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
```python
def group_by(self, member, limit=10, descending=True, id_field=True):
    """
    Aggregations
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-aggregations.html
    :param member: {string} The property name of the document.
    :param limit: {int} The number of returns.
    :param descending: {bool} Is sorted by descending?
    :param id_field: {bool} There is '-' in id, and ElasticSearch will .split() it.
                                    If this param is true, asahi will join that together.
    :returns: {list}
        {list}[{dict}]
        {
            doc_count: {int},
            key: 'term'
        }
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
+ BooleanProperty
+ FloatProperty
+ DateTimeProperty
+ ListProperty
+ DictProperty
+ ReferenceProperty


##Requirement
>```bash
$ git submodule update --init
$ pip3 install -r pip_requirements.txt
```



##unit-test
>```bash
$ python3 test.py
```



##Note
>There are issues about ElasticSearch.  
If your OS X is 10.9.3, your default Java is 1.6. ElasticSearch 1.2.0 required Java 1.7.
Run ElasticSearch 1.2.0 on Java 1.6 will pop the message like this:
```
 Exception in thread "main" java.lang.UnsupportedClassVersionError: org/elasticsearch/bootstrap/Elasticsearch : Unsupported major.minor version 51.0
 at java.lang.ClassLoader.defineClass1(Native Method)
 at java.lang.ClassLoader.defineClassCond(ClassLoader.java:631)
 at java.lang.ClassLoader.defineClass(ClassLoader.java:615)
 at java.security.SecureClassLoader.defineClass(SecureClassLoader.java:141)
 at java.net.URLClassLoader.defineClass(URLClassLoader.java:283)
 at java.net.URLClassLoader.access$000(URLClassLoader.java:58)
 at java.net.URLClassLoader$1.run(URLClassLoader.java:197)
 at java.security.AccessController.doPrivileged(Native Method)
 at java.net.URLClassLoader.findClass(URLClassLoader.java:190)
 at java.lang.ClassLoader.loadClass(ClassLoader.java:306)
 at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:301)
 at java.lang.ClassLoader.loadClass(ClassLoader.java:247)
Could not find the main class: org.elasticsearch.bootstrap.Elasticsearch.  Program will exit.
```



##References
>+ [elasticsearch-queries](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-queries.html)
