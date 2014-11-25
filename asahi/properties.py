from datetime import datetime
from couchdbkit import schema
from .exceptions import BadValueError


class Property(object):
    def __init__(self, default=None, is_required=False):
        self.document_class = None
        self.name = None
        self.default = default
        self.is_required=is_required

    def __get__(self, document_instance, document_class):
        if document_instance is None:
            return self

        value = document_instance._document.get(self.name)
        if value is None:
            return value
        return self._to_python(value)

    def __set__(self, document_instance, value):
        if value is None:
            if self.is_required:
                raise BadValueError('%s is required' % self.name)
            document_instance._document[self.name] = None
        else:
            document_instance._document[self.name] = self._to_json(value)

    def __property_config__(self, document_class, property_name):
        """
        Setup the property.
        :param document_class: {Document} The document class.
        :param property_name: {string} The property name in the document.
        :return:
        """
        self.document_class = document_class
        if self.name is None:
            self.name = property_name

    def _to_python(self, value):
        """
        Convert the value to Python format.
        :param value:
        :return:
        """
        return unicode(value)
    def _to_json(self, value):
        """
        Convert the value to ElasticSearch format.
        :param value:
        :return:
        """
        return unicode(value)

class StringProperty(Property):
    _to_python = unicode
    _to_json = unicode

class IntegerProperty(Property):
    _to_python = int
    _to_json = int

class LongProperty(Property):
    _to_python = long
    _to_json = long

class FloatProperty(Property):
    _to_python = float
    _to_json = float

class BooleanProperty(Property):
    _to_python = bool
    _to_json = bool

class DateTimeProperty(Property):
    def __init__(self, is_auto_now=False, *args, **kwargs):
        super(DateTimeProperty, self).__init__(*args, **kwargs)
        self.is_auto_now = is_auto_now

    def _to_python(self, value):
        """
        Convert value to python format.
        :param value: {datetime}, {string}
        :return: {datetime}
        """
        if isinstance(value, basestring):
            try:
                value = value.split('.', 1)[0] # strip out microseconds
                value = value[0:19] # remove timezone
                value = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
            except ValueError, e:
                raise ValueError('Invalid ISO date/time %r [%s]' % (value, str(e)))
        return value
    def _to_json(self, value):
        """
        Convert value to json format.
        :param value: {datetime}, {string}
        :return: {string}
        """
        if isinstance(value, basestring):
            return value
        return value.replace(microsecond=0).isoformat() + 'Z'


# Property = schema.Property
DecimalProperty = schema.DecimalProperty
DateProperty = schema.DateProperty
TimeProperty = schema.TimeProperty
ListProperty = schema.ListProperty
DictProperty = schema.DictProperty
StringDictProperty = schema.StringDictProperty
StringListProperty = schema.StringListProperty
SchemaDictProperty = schema.SchemaDictProperty
SetProperty = schema.SetProperty
