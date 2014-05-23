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



##References
>+ [elasticsearch-queries](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-queries.html)
