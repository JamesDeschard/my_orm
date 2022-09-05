from models import *

# Tests with book class


# Save object to database

# Get Object from database

if __name__ == '__main__':  
    
    print('#############################################')
    print('TESTING ORM')
    print('#############################################')
    
    # Test Create 
      
    Book.objects.create(title="Oliver Twist", author="Charles Dickens")
    Book.objects.create(title="The Lord of the Flies", author="William Golding")
    b = Book(title="The Hobbit", author="J.R.R. Tolkien")
    b.save()
    x = Book(title="Monte Cristo", author="Alexandre Dumas")
    x.save()

    
    for book in Book.objects.all():
        print(book.title, book.id)
        
    # Test Update
    
    a = Book(title="The war of the worlds", author="H.G. Wells")
    a.save()
    test = Book.objects.get(title="The war of the worlds", author="H.G. Wells")
    test.update(title="Updated Title", author="Updated Author")
    test = Book.objects.get(title="Updated Title", author="Updated Author")
    
    Book.objects.create(title="Vikings", author="Michael Hirst")
    
    # Test Delete 
    
    for book in Book.objects.all():
        book.delete()
        
    print('#############################################')
    print('ALL TESTS PASSED')
    print('#############################################')
    
    
