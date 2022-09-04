from fields import CharField, IntegerField
from orm import BaseModel


# class Child(BaseModel):
#     name = CharField(max_length=255)
#     surname = CharField(max_length=255)
#     age = IntegerField()

class Book(BaseModel):
    title = CharField(max_length=255)
    author = CharField(max_length=255)

# class Student(BaseModel):
#     title = CharField(max_length=255)
#     author = CharField(max_length=255)
    