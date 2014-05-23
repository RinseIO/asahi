import unittest
from couchdbkit import schema
from asahi import properties


class TestAsahiProperties(unittest.TestCase):
    def test_asahi_properties_property(self):
        self.assertIs(properties.Property, schema.Property)
    def test_asahi_properties_string_property(self):
        self.assertIs(properties.StringProperty, schema.StringProperty)
    def test_asahi_properties_integer_property(self):
        self.assertIs(properties.IntegerProperty, schema.IntegerProperty)
    def test_asahi_properties_decimal_property(self):
        self.assertIs(properties.DecimalProperty, schema.DecimalProperty)
    def test_asahi_properties_boolean_property(self):
        self.assertIs(properties.BooleanProperty, schema.BooleanProperty)
    def test_asahi_properties_float_property(self):
        self.assertIs(properties.FloatProperty, schema.FloatProperty)
    def test_asahi_properties_date_time_property(self):
        self.assertIs(properties.DateTimeProperty, schema.DateTimeProperty)
    def test_asahi_properties_date_property(self):
        self.assertIs(properties.DateProperty, schema.DateProperty)
    def test_asahi_properties_time_property(self):
        self.assertIs(properties.TimeProperty, schema.TimeProperty)
    def test_asahi_properties_schema_property(self):
        self.assertIs(properties.SchemaProperty, schema.SchemaProperty)
    def test_asahi_properties_schema_list_property(self):
        self.assertIs(properties.SchemaListProperty, schema.SchemaListProperty)
    def test_asahi_properties_list_property(self):
        self.assertIs(properties.ListProperty, schema.ListProperty)
    def test_asahi_properties_dict_property(self):
        self.assertIs(properties.DictProperty, schema.DictProperty)
    def test_asahi_properties_string_dict_property(self):
        self.assertIs(properties.StringDictProperty, schema.StringDictProperty)
    def test_asahi_properties_string_list_property(self):
        self.assertIs(properties.StringListProperty, schema.StringListProperty)
    def test_asahi_properties_schema_dict_property(self):
        self.assertIs(properties.SchemaDictProperty, schema.SchemaDictProperty)
    def test_asahi_properties_set_property(self):
        self.assertIs(properties.SetProperty, schema.SetProperty)
        