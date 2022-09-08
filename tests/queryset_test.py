import random
import string
import unittest

from .test_models import *


def get_random_name(length):
    return ''.join(random.choice(string.ascii_letters).capitalize() for i in range(length))


def create_multiple_authors(amount):
    for i in range(amount):
        author = Author(
            name=get_random_name(random.randrange(3, 10)), 
            surname=get_random_name(random.randrange(3, 10))
        )
        author.save()
        
class TestQuerySets(unittest.TestCase):  
    
    def test_all(self):      
        create_multiple_authors(2)
        _all = Author.objects.all()
        _all = [author for author in _all]
        
        self.assertEqual(len(_all), 2)
        
        Author(name='John', surname='Doe').save()
        Author(name='Jane', surname='Doe').save()
        
        for i in Author.objects.all().filter(surname='Doe'):
            self.assertEqual(i.surname, 'Doe')
        
        for i in Author.objects.all().filter(surname='Doe').filter(name='John'):
            self.assertEqual(i.name, 'John')

        first_test = Author.objects.all().filter(surname='Doe').first()
        self.assertEqual(first_test.name, 'John')

        for author in Author.objects.all():
            author.delete()
            
        Author(name='John', surname='Doe').save()
        Author(name='Jane', surname='Doe').save()
        
        jane = Author.objects.all().exclude(name='John')
        self.assertEqual(jane[0].name, 'Jane')
        
        for author in Author.objects.all():
            author.delete()
        
        
if __name__ == '__main__':  
    unittest.main()
