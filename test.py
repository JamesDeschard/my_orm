from models import *

# Tests with book class


# Save object to database

# Get Object from database

if __name__ == '__main__':
    # b = Book.objects.delete(title="The Lord of the Flies", author="William Golding")
    
    # a = Book(title="The war of the worlds", author="H.G. Wells")
    # print(a)
    # a.save()
    # b = Book.objects.read(title="The war of the worlds", author="H.G. Wells")
    # print(b.title, b.author)
    # b = Book.objects.update(title="The Lord of the Flies", author="William Golding")

    # b = Book.objects.read(title="The Lord of the Flies", author="William Golding")
    # print(b.title, b.author)
    # print(b)
    # b.delete()
    
    # c = Book.objects.create(title="Oliver Twist", author="Charles Dickens")
    # c = Book.objects.read(title="Oliver Twist", author="Charles Dickens")
    # c.objects.delete(title="Oliver Twist", author="Charles Dickens")
    
    
    
    # Book.objects.create(title="Oliver Twist", author="Charles Dickens")
    # Book.objects.create(title="The Lord of the Flies", author="William Golding")
    # a = Book(title="The war of the worlds", author="H.G. Wells")
    # a.save()
    # b = Book(title="The Hobbit", author="J.R.R. Tolkien")
    # b.save()
    # x = Book(title="Monte Cristo", author="Alexandre Dumas")
    # x.save()

    
    # for book in Book.objects.all():
    #     print(book.title, book.id)
        
    # Test Update
    
    test = Book.objects.read(title="The war of the worlds", author="H.G. Wells")
    print(test)
    test.update(title="Updated Title", author="Updated Author")
    test = Book.objects.read("Updated Title", author="Updated Author")
    print(test.title, test.author)
    
    for book in Book.objects.all():
        print(book)
        book.delete()
    
    
