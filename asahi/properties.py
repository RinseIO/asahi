from couchdbkit import schema


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
        return self.__to_python(value)

    def __set__(self, document_instance, value):
        document_instance._document[self.name] = self.__to_json(value)

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

    def __to_python(self, value):
        """
        Convert the value to Python format.
        :param value:
        :return:
        """
        return unicode(value)
    def __to_json(self, value):
        """
        Convert the value to ElasticSearch format.
        :param value:
        :return:
        """
        if value is None:
            return value
        return unicode(value)

class StringProperty(Property):
    __to_python = unicode
    __to_json = unicode

class IntegerProperty(Property):
    __to_python = int
    __to_json = int

class LongProperty(Property):
    __to_python = long
    __to_json = long


# Property = schema.Property
DecimalProperty = schema.DecimalProperty
BooleanProperty = schema.BooleanProperty
FloatProperty = schema.FloatProperty
DateTimeProperty = schema.DateTimeProperty
DateProperty = schema.DateProperty
TimeProperty = schema.TimeProperty
SchemaProperty = schema.SchemaProperty
SchemaListProperty = schema.SchemaListProperty
ListProperty = schema.ListProperty
DictProperty = schema.DictProperty
StringDictProperty = schema.StringDictProperty
StringListProperty = schema.StringListProperty
SchemaDictProperty = schema.SchemaDictProperty
SetProperty = schema.SetProperty
