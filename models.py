from orm import BaseModel
from fields import CharField, IntegerField


class Child(BaseModel):
    name = CharField(max_length=255)
    surname = CharField(max_length=255)
    age = IntegerField()

# class Book(BaseModel):
#     title = CharField(max_length=255)
#     author = CharField(max_length=255)

class Student(BaseModel):
    title = CharField(max_length=255)
    author = CharField(max_length=255)
    