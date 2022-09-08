import importlib

from .utils import get_class_module
from .connect import ExecuteQuery


class QuerySetSearch:
    """
    An extension of the QuerySet class that allows for filtering and ordering of the queryset.

    ...

    Attributes
    ----------

    Methods
    -------

    """
    
    def __init__(self, cached_result) -> None:
        self.cached_result = cached_result
        
    def update_cache(self, sql_extension):
        if not 'WHERE' in self.cached_result:
            self.cached_result = f' {self.cached_result} WHERE {sql_extension}'
        else:
            self.cached_result = f' {self.cached_result} AND {sql_extension}'
    
    def filter_or_exclude(self, type, **kwargs):
        sql_extension = "".join([f"{key} {type} '{value}'" for key, value in kwargs.items()])
        self.update_cache(sql_extension)
        self.hit_db()
        return self
        
    def filter(self, **kwargs):
        return self.filter_or_exclude('=', **kwargs)
    
    def exclude(self, **kwargs):
        return self.filter_or_exclude('!=', **kwargs)
        
    def first(self):
        self.cached_result = f' {self.cached_result} LIMIT 1'
        self.hit_db()
        return self.queryset[0] if self.queryset else None
    
    def order_by(self, order):
        pass
        # self.cached_result = f' {self.cached_result} ORDER BY {order}'
        # self.hit_db()
        # return self
    

class QuerySet(QuerySetSearch):
    """
    A class used to represent the result of a Query.
    Queries are evaluated lazily.
    They don't hit the database until you iterate over them or call them with a method from QuerySetSerach.

    ...

    Attributes
    ----------
    query : str
        The query to be executed
    model_class : class
        The model class to be used to create the queryset

    Methods
    -------
    check_for_relation(self)
        Checks wether the model has a foreign key relation.
        If it does, returns the field name and the relations model class.
    
    create(self, get_unique=False)
        Caches the query. If get_unique is True, it executes the query and returns the first result.
        Otherwise, it returns itself.
        
    hit_db(self)
        Executes the query and appends the results to the queryset.
    """
    
    def __init__(self, query, model_class) -> None:
        super().__init__(cached_result=str())
        self.query = query
        self.model_class = model_class
        
        self.queryset = list()
        self.index = 0

    def __iter__(self):
        self.hit_db()
        return self
    
    def __next__(self):
        if self.index < len(self.queryset):
            result = self.queryset[self.index]
            self.index += 1
            return result
        raise StopIteration
    
    def __len__(self):
        return len(self.queryset)
    
    def __getitem__(self, index):
        return self.queryset[index]
    
    def check_for_relation(self):
        for field_name, field_value in self.model_class.fields.items():
            if field_value.__class__.__name__ == 'ForeignKey':
                module = get_class_module(field_name)
                foreignkey = importlib.import_module(module)
                foreignkey = getattr(foreignkey, field_name.capitalize())
                return field_name, foreignkey
        return False, False

    def create(self, get_unique=False) -> list: 
        if not self.cached_result:
            self.cached_result = self.query  
                  
        if get_unique:
            self.hit_db()
            return self.queryset[0] if self.queryset else None
        
        else:
            return self

    def hit_db(self):
        query = ExecuteQuery(self.cached_result).execute(read=True)
        if not query:
            return
        
        self.queryset = list()
        
        for q in query:
            obj_attrs = dict()
            foreign_key_field, foreign_key_model = self.check_for_relation()
            
            for key, value in zip(self.model_class.fields.keys(), q):
                if foreign_key_field and key == foreign_key_field:
                    obj_attrs[key] = foreign_key_model.objects.get(id=value)
                else:
                    obj_attrs[key] = value
                    
            self.queryset.append(self.model_class(**obj_attrs))
            