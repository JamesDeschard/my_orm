from db_link.fields import CharField, ForeignKey
from db_link.orm import BaseModel

# Add your test models here.


class Author(BaseModel):
    name = CharField(max_length=255)
    surname = CharField(max_length=255)

class Book(BaseModel):
    title = CharField(max_length=255)
    author = ForeignKey(Author, on_delete='CASCADE')
