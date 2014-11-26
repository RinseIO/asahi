import unittest
from asahi import db
from asahi.document import Document
from asahi.properties import *


class TestAsahiDB(unittest.TestCase):
    def test_asahi_db_document(self):
        self.assertIs(db.Document, Document)
        
    def test_asahi_db_property_property(self):
        self.assertIs(db.Property, Property)
    def test_asahi_db_property_string_property(self):
        self.assertIs(db.StringProperty, StringProperty)
    def test_asahi_db_property_integer_property(self):
        self.assertIs(db.IntegerProperty, IntegerProperty)
    def test_asahi_db_property_boolean_property(self):
        self.assertIs(db.BooleanProperty, BooleanProperty)
    def test_asahi_db_property_float_property(self):
        self.assertIs(db.FloatProperty, FloatProperty)
    def test_asahi_db_property_date_time_property(self):
        self.assertIs(db.DateTimeProperty, DateTimeProperty)
    def test_asahi_db_property_list_property(self):
        self.assertIs(db.ListProperty, ListProperty)
    def test_asahi_db_property_dict_property(self):
        self.assertIs(db.DictProperty, DictProperty)
    def test_asahi_db_property_reference_property(self):
        self.assertIs(db.ReferenceProperty, ReferenceProperty)
