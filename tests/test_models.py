from orm.orm_base_model import BaseModel

# Add your test models here.


class Author(BaseModel):
    name = BaseModel.CharField(max_length=255)
    surname = BaseModel.CharField(max_length=255)

class Book(BaseModel):
    title = BaseModel.CharField(max_length=255)
    author = BaseModel.ForeignKey(Author, on_delete='CASCADE')
