import random
import string
import unittest

from .test_models import *


def get_random_name(length):
    return ''.join(random.choice(string.ascii_letters).capitalize() for i in range(length))

        
class TestQuerySets(unittest.TestCase):  
    pass
    def test_all(self):  
        for i in Author.objects.all():
                i.delete()

        for i in range(10):
            author = Author(
                name=get_random_name(random.randrange(3, 10)), 
                surname=get_random_name(random.randrange(3, 10))
            ).save()
        
        _all = Author.objects.all()

        self.assertEqual(len(_all), 0) # Lazy loading
        self.assertEqual(len(list(_all)), 10) # Lazy loading
        
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
