import logging
from sqlite3 import TimeFromTicks
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
        author = Author.objects.get(name='John').delete()
        author = Author.objects.get(name='John')
        self.assertEqual(author, None)
    
    def test_foreign_key(self):
        create_author()
        author = Author.objects.get(name='John', surname='Doe')
        book = Book(title='Test', author=author).save()
        book = Book.objects.get(title='Test')
        self.assertEqual(book.author.name, 'John')
        author.delete()
        
        book = Book.objects.get(title='Test')
        author = Author.objects.get(name='John')
        self.assertEqual(book, None)
        self.assertEqual(author, None)
        
        create_author()
        author = Author.objects.get(name='John')
        for i in range(5):
            book = Book(title=f'Test_{i}', author=author)
            book.save()
        
        for book in Book.objects.all():
            self.assertEqual(book.author.id, author.id)
            book.delete()
        
        author.delete()
    
    def test_one_to_one(self):
        PassPortOwner(name='Bob').save()
        passport_owner = PassPortOwner.objects.get(name='Bob')
        passport = Passport(owner=passport_owner, number='123456789').save()
        passport = Passport.objects.get(number='123456789')
        self.assertEqual(passport.owner.name, passport_owner.name)  
        # Making a second passport will call a UNIQUE constraint violation

    def test_many_to_man(self):
        Student(name='David').save()
        Student(name='James').save()
        Student(name='Charles').save()

        Course(title='Python').save()
        # Course(title='C#').save()
        # Course(title='Java').save()
        student_1 = Student.objects.get(name='David')
        student_2 = Student.objects.get(name='James')
        student_3 = Student.objects.get(name='Charles')
        
        course_1 = Course.objects.get(title='Python')
        

        course_1.students.add(student_1, student_2, student_3)
        
        self.assertEqual(len(list(course_1.students.all())), 3)
        
        for s in Student.objects.all():
            s.delete()
        
        for c in Course.objects.all():
            c.delete()
        
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
    
    pass


if __name__ == '__main__':  
    unittest.main()
    