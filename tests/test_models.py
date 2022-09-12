from orm.orm_base_model import BaseModel

# Add your test models here.

class Person(BaseModel):
    name = BaseModel.CharField(max_length=50, default='Bob')
    surname = BaseModel.CharField(max_length=50, null=True)
    test = BaseModel.CharField(max_length=50, blank=True)
    age = BaseModel.IntegerField(default=0)


class PassPortOwner(BaseModel):
    name = BaseModel.CharField(max_length=50)


class Passport(BaseModel):
    owner = BaseModel.OneToOneField(PassPortOwner, on_delete='CASCADE')
    number = BaseModel.CharField(max_length=50)


class Author(BaseModel):
    name = BaseModel.CharField(max_length=255)
    surname = BaseModel.CharField(max_length=255)


class Book(BaseModel):
    title = BaseModel.CharField(max_length=255)
    author = BaseModel.ForeignKey(Author, on_delete='CASCADE')
    

class Student(BaseModel):
    name = BaseModel.CharField(max_length=255)


class Course(BaseModel):
    title = BaseModel.CharField(max_length=255)
    students = BaseModel.ManyToManyField(Student, on_delete='CASCADE')



