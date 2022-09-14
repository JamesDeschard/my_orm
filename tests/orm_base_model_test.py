import logging
import unittest

from .test_models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TESTING')


class TestCRUD(unittest.TestCase):
    def test_create(self):
        author = Author(name='John', surname='Doe')
        author.save()
        self.assertEqual(author.name, 'John')
        self.assertEqual(author.surname, 'Doe')
        
        logger.info('TestCRUD.test_create() ----> \u2713')

    def test_delete(self):
        author = Author.objects.get(name='John').delete()
        self.assertEqual(author, None)
        
        logger.info('TestCRUD.test_delete() ----> \u2713')
        
    def test_update(self):
        author = Author(name='John', surname='Doe').save()
        author.update(name='Jane')
        author = Author.objects.get(name='Jane')
        self.assertEqual(author.name, 'Jane')

        author.name = 'John'
        author.update()
        self.assertEqual(author.name, 'John')
        author.delete() 
        
        logger.info('TestCRUD.test_update() ----> \u2713')
    
    
class TestRelations(unittest.TestCase):
    def test_one_to_one(self):
        passport_owner_1 = PassPortOwner(name='Bob').save()
        passport_owner_2 = PassPortOwner(name='John').save()
        
        passport_1 = Passport(owner=passport_owner_1, number='123456789').save()
        passport_2 = Passport(owner=passport_owner_2, number='987654321').save()
        print(passport_1.owner.name)
        print(passport_2.owner.name)
        
        self.assertEqual(passport_1.owner.name, passport_owner_1.name)  
        # Making a second passport will call a UNIQUE constraint violation
        
        logger.info('TestRelations.test_one_to_one() ----> \u2713')
        
    def test_foreign_key(self):
        author = Author(name='John', surname='Doe').save()
        book = Book(title='Test', author=author).save()
        self.assertEqual(book.author.name, 'John')
        author.delete()
        
        book = Book.objects.get(title='Test')
        author = Author.objects.get(name='John')
        self.assertEqual(book, None)
        self.assertEqual(author, None)
        
        author = Author(name='John', surname='Doe').save()

        for i in range(5):
            book = Book(title=f'Test_{i}', author=author)
            book.save()
        
        for book in Book.objects.all():
            self.assertEqual(book.author.id, author.id)
            book.delete()
        
        author.delete()
        
        logger.info('TestRelations.test_foreign_key() ----> \u2713')

    def test_many_to_man(self):
        Student(name='David').save()
        Student(name='James').save()
        Student(name='Charles').save()

        Course(title='Python').save()
        Course(title='C#').save()
        
        student_1 = Student.objects.get(name='David')
        student_2 = Student.objects.get(name='James')
        student_3 = Student.objects.get(name='Charles')
        
        course_1 = Course.objects.get(title='Python')
        course_2 = Course.objects.get(title='C#')
        
        # Add students to courses
        
        course_1.students.add(student_1, student_2, student_3)
        course_2.students.add(student_1)
    
        
        # Should return all courses for student 1
        student_1_courses = list(student_1.course_set.all())

        self.assertEqual(list(student_1_courses)[1].title, 'C#')
        
        self.assertEqual(list(course_1.students.all())[2].name, 'Charles')
        print([s.name for s in course_1.students.all()])
        self.assertEqual(list(course_2.students.all())[0].name, 'David')
        
        # Create a student and add to a course 
        
        course_2.students.create(name='John')
        self.assertEqual(list(course_2.students.all())[1].name, 'John')
        
        for s in Student.objects.all():
            s.delete()
        
        for c in Course.objects.all():
            c.delete()
            
        logger.info('TestRelations.test_many_to_man() ----> \u2713')


if __name__ == '__main__':  
    unittest.main()
    