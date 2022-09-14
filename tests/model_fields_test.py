import unittest
import logging

from .test_models import *

class TestFields(unittest.TestCase):
    def test_null(self):
        person = Person().save()
        self.assertEquals('Bob', person.name)
        
        person = Person(name='John').save()
        person = Person(name='Foo', surname='Bar').save()
        person = Person(name='Foo', surname='Bar', test='TestyTest', age=28).save()
        
        for i, person in enumerate(Person.objects.all()):
            if i < 3:
                self.assertEquals(person.test, '') # Default blank
                self.assertEquals(person.age, 0)   # Default 0
            elif i < 2:
                self.assertEquals(person.surname, None) # Default null
                
            person.delete()
            