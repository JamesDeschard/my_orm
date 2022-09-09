import unittest
import logging

from .test_models import *

class TestFields(unittest.TestCase):
    
    def test_null(self):
        person = Person()
        person.save()
        person = Person.objects.get(name='Bob')
        self.assertAlmostEquals('Bob', person.name)
        
        person = Person(name='John')
        person.save()
        
        person = Person(name='Foo', surname='Bar')
        person.save()
        
        person = Person(name='Foo', surname='Bar', test='TestyTest', age=28)
        person.save()
        
        for i in Person.objects.all():
            i.delete()