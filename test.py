import logging
import unittest
import string
import random

from models import *


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TESTING')


def get_random_name(length):
    return ''.join(random.choice(string.ascii_letters).capitalize() for i in range(length))


def create_multiple_authors(amount):
    for i in range(amount):
        author = Author(
            name=get_random_name(random.randrange(3, 10)), 
            surname=get_random_name(random.randrange(3, 10))
        )
        author.save()


def create_author():
    author = Author(name='John', surname='Doe')
    author.save()


class TestCRUD(unittest.TestCase):
    
    def test_create(self):
        create_author()
        author = Author.objects.get(name='John', surname='Doe')
        self.assertEqual(author.name, 'John')
        self.assertEqual(author.surname, 'Doe')

    def test_delete(self):
        author = Author.objects.get(name='John')
        author.delete()
        author = Author.objects.get(name='John')
        self.assertEqual(author, None)
    
    def test_foreign_key(self):
        create_author()
        author = Author.objects.get(name='John', surname='Doe')
        book = Book(title='Test', author=author)
        book.save()
        book = Book.objects.get(title='Test')
        self.assertEqual(book.author.name, 'John')
        author.delete()
        
        book = Book.objects.get(title='Test')
        author = Author.objects.get(name='John')
        self.assertEqual(book, None)
        self.assertEqual(author, None)
        
    def test_update(self):
        create_author()
        author = Author.objects.get(name='John')
        author.update(name='Jane')
        author = Author.objects.get(name='Jane')
        self.assertEqual(author.name, 'Jane')

        author.name = 'John'
        author.update()
        self.assertEqual(author.name, 'John')
        author.delete() 


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
    