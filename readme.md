# How does it work? Building a small custom ORM

## Quick example:

Create a file called `models.py` or any other suitable name. Like so:

``` python
from orm.orm_base_model import BaseModel

# Create your models here.

class Author(BaseModel):
    name = BaseModel.CharField(max_length=255)
    surname = BaseModel.CharField(max_length=255)
```

`name` and `surname` are fields of the model. Each field is specified as a class attribute, and each attribute maps to a database column.
Will generate the following SQL code:

``` sql
CREATE TABLE IF NOT EXISTS author (
    id INTEGER PRIMARY KEY,
    name VARCHAR (255) , 
    surname VARCHAR (255) 
    );
```

## Using models

Once you have defined your models, you need to tell the ORM you’re going to use those models. Do this by editing your settings file and changing the `CURRENT_MODELS` setting to add the name your models file.
You must also specify your database settings in the `DB_SETTINGS` variable. If you connect using SQLite the database will be automatically created on your first migration.
Run `python manage.py migrate` to generate the SQL and create your database.

## Modify your models

TO DO.

## Fields

### Fields

This little project currently supports:
- CharField
- IntegerField
- BooleanField

### Field Options

- **blank**
If `True`, Django will store empty values as NULL in the database. Default is False.
- **null**
If `True`, the field is allowed to be blank. Default is False.
- **default**
The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created.
- **unique**
If `True`, this field must be unique throughout the table.


## Relationships

All relations have a `on_delete` attribute (currently only `CASCADE` is supported).

### OneToOneField

#### Example:

``` python 
class PassPortOwner(BaseModel):
    name = BaseModel.CharField(max_length=50)


class Passport(BaseModel):
    owner = BaseModel.OneToOneField(PassPortOwner, on_delete='CASCADE')
    number = BaseModel.CharField(max_length=50)
```

Let's create somme relations:

``` python

passport_owner_1 = PassPortOwner(name='Bob').save()
passport_owner_2 = PassPortOwner(name='John').save()

passport_1 = Passport(owner=passport_owner_1, number='123456789').save()
passport_2 = Passport(owner=passport_owner_2, number='987654321').save()

print(passport_1.owner.name)
print(passport_2.owner.name)

# Will return:
# Bob
# John
```
Adding another passport to a user who already had one will raise a ``UNIQUE constraint failed `` error.

``` python
passport_3 = Passport(owner=passport_owner_1, number='98483094830').save()

# Will return:
# sqlite3.IntegrityError: UNIQUE constraint failed: passport.owner
```

### ManyToOne (ForeignKey) (1toN)

To define a many-to-one relationship, use the `ForeignKey` field:

``` python 
class Author(BaseModel):
    name = BaseModel.CharField(max_length=255)
    surname = BaseModel.CharField(max_length=255)


class Book(BaseModel):
    title = BaseModel.CharField(max_length=255)
    author = BaseModel.ForeignKey(Author, on_delete='CASCADE')
```

Let's create somme relations:

``` python
author = Author(name='John', surname='Doe').save()

for i in range(5):
    book = Book(title=f'Test_{i}', author=author)
    book.save()
    print(book.author.name, book.name)

# Will return:
# John Test_0
# John Test_1
# John Test_2
# John Test_3
# John Test_4
```


### ManyToManyField(NtoN)

To define a many-to-many relationship, use `ManyToManyField`.

``` python
class Student(BaseModel):
    name = BaseModel.CharField(max_length=255)


class Course(BaseModel):
    title = BaseModel.CharField(max_length=255)
    students = BaseModel.ManyToManyField(Student, on_delete='CASCADE')
```

Create some students:
``` python
Student(name='David').save()
Student(name='James').save()
Student(name='Charles').save()
```
... and some courses:

``` python
Course(title='Python').save()
Course(title='C#').save()
```

Add some students to a course:

``` python
course_1.students.add(student_1, student_2, student_3)
course_2.students.add(student_1)
```

Get all the courses for student_1: 

``` python
student_1_courses = list(student_1.course_set.all())
print([c.title for c in student_1_courses])

# Will return:
# ['Python', 'C#']
```

Or all the students in a course:

``` python
course_1_students = list(course_1.students.all())
print([s.name for s in course_1.students.all()])

# Will return:
# ['David', 'James', 'Charles']
```

You can also create a student and add him to a class.

``` python
course_1.students.create(name='Reacher')
print(list(course_1.students.all()))

# Will return:
# ['David', 'James', 'Charles', 'Reacher']
```

# QuerySets

A `QuerySet` object is returned by the manager (base manager or relation manager) `all()` methods.
For example:

``` python
Author(name='John', surname='Doe').save()
Author(name='Jane', surname='Doe').save()
Author(name='James', surname='Deschard').save()
print(type(author.objects.all()))
print(list(author.objects.all()))

# Will return:
# <class 'orm.queryset.QuerySet'>
# [<Author: [id=1, name=John, surname=Doe]>, <Author: [id=2, name=Jane, surname=Doe]>, <Author: [id=3, name=James, surname=Deschard]>]
```

## Evaluating a QuerySet

QuerySets are evaluated lazily meaning they only hit the database when called upon. Currently querysets can
be evaluated by:

- Iterating over them (for loop or using `list(queryset)`)
- Calling a method on the queryset (filter or exclude)

## QuerySet methods

A ``QuerySet`` method returns another ``QuerySet`` object even if ``len(queryset) == 1 is True``. Currently you can use:

### filter()

``filter(*args, **kwargs)``
Returns a new QuerySet containing objects that match the given lookup parameters.
Parameters must match with the model.


### exclude()
``exclude(*args, **kwargs)``
Returns a new QuerySet containing objects that do not match the given lookup parameters.
Parameters must match with the model.

### More to come...


