from models import *

# Tests with book class


# Save object to database

# Get Object from database

if __name__ == '__main__':
    # Book.objects.create(title="The Alchemist", author="Paulo Coelho")
    x = Book.objects.read(title="The Alchemist")
    print(x.id)
    # Book.objects.delete(title="The Alchemist")
