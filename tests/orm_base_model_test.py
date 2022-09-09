import logging
import unittest

from .test_models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TESTING')


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


if __name__ == '__main__':  
    unittest.main()
    