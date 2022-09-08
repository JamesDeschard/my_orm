from db_link.fields import CharField, IntegerField, ForeignKey

from db_link.orm import BaseModel

class Person(BaseModel):
    name = CharField(max_length=255)

# Create your models here.