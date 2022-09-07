from multiprocessing.util import sub_warning
from fields import CharField, IntegerField, ForeignKey
from orm import BaseModel

class Author(BaseModel):
    name = CharField(max_length=255)
    surname = CharField(max_length=255)

class Book(BaseModel):
    title = CharField(max_length=255)
    author = ForeignKey(Author, on_delete='CASCADE')

