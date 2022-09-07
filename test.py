import logging
import unittest
import string
import random

from models import *


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TESTING')


class TestCRUD(unittest.TestCase):
    
    def get_random_name(self, length):
        return ''.join(random.choice(string.ascii_letters).capitalize() for i in range(length))

    
    def create_multiple_authors(self, amount):
        for i in range(amount):
            author = Author(
                name=self.get_random_name(random.randrange(3, 10)), 
                surname=self.get_random_name(random.randrange(3, 10))
            )
            author.save()
    
    def create_author(self):
        author = Author(name='John', surname='Doe')
        author.save()
    
    def test_create(self):
        author = Author(name='John', surname='Doe')
        author.save()
        self.assertEqual(author.name, 'John')
        self.assertEqual(author.surname, 'Doe')

    def test_delete(self):
        author = Author.objects.get(name='John')
        author.delete()
        author = Author.objects.get(name='John')
        self.assertEqual(author, None)
    
    def test_foreign_key(self):
        self.create_author()
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
        self.create_author()
        author = Author.objects.get(name='John')
        author.update(name='Jane')
        author = Author.objects.get(name='Jane')
        self.assertEqual(author.name, 'Jane')

        author.name = 'John'
        author.update()
        self.assertEqual(author.name, 'John')
        author.delete() 
    
    def test_all(self):
        for author in Author.objects.all():
            author.delete()
        self.create_multiple_authors(5)
        _all = Author.objects.all()
        print(_all.filter())
        self.assertEqual(len(_all), 5)
        for author in Author.objects.all():
            author.delete()
        self.assertEqual(len(Author.objects.all()), 0)

    

if __name__ == '__main__':  
    unittest.main()
    
    
    
