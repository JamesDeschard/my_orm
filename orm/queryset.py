import copy
import inspect

from .db_connections import ExecuteQuery
from .sql_queries import ModelManagerQueries
from .utils import get_relation_classes_without_relation_fields, relations

RELATIONS = relations()


class QuerySetSearch:
    """
    This class is a wrapper for the QuerySet class. It is used to filter the queryset.
    """
    def __init__(self, cached_result) -> None:
        self.cached_result = cached_result
        
    def update_cache(self, sql_extension):
        if not 'WHERE' in self.cached_result:
            self.cached_result = f' {self.cached_result} WHERE {sql_extension}'
        else:
            self.cached_result = f' {self.cached_result} AND {sql_extension}'
    
    def filter_or_exclude(self, operator, **kwargs):
        sql_extension = "".join([f"{key} {operator} '{value}'" for key, value in kwargs.items()])
        self.update_cache(sql_extension)
        self.hit_db()
        return self
        
    def filter(self, **kwargs):
        return self.filter_or_exclude(operator='=', **kwargs)
    
    def exclude(self, **kwargs):
        return self.filter_or_exclude(operator='!=', **kwargs)
        
    def first(self):
        self.cached_result = f' {self.cached_result} LIMIT 1'
        self.hit_db()
        return self.queryset[0] if self.queryset else None
    
    def order_by(self, order):
        pass
        # self.cached_result = f' {self.cached_result} ORDER BY {order}'
        # self.hit_db()
        # return self
    
    
class FieldRelationManager:    
    """
    This class manages many to many relations for the model.
    It is accessible from the model attribute which has a many to many field.
    """
    def __init__(self, id, r_1, r_2, r_tree) -> None:
        self.id = id
        self.table_1 = r_1.lower()
        self.table_2 = r_2.lower()
        
        self.relation_class = r_tree.get(r_2)
        self.junction_table = f'{self.table_1}_{self.table_2}'
    
    def add(self, *args):
        for obj in args:
            query = ModelManagerQueries().field_manager_add(
                self.junction_table,
                self.table_1,
                self.table_2, 
                obj.id, 
                self.id
            )
            ExecuteQuery(query).execute()

    def all(self):
        rows = f', {self.table_1}.'.join(self.relation_class.fields.keys())
        query = ModelManagerQueries().field_manager_all(
            self.junction_table, 
            self.table_1, 
            self.table_2, 
            self.id, 
            rows
        )  
                      
        return QuerySet(query, self.relation_class).build()

    def create(self, **kwargs):
        self.relation_class.objects.create(**kwargs)
        get_created_class = self.relation_class.objects.get(**kwargs)
        self.add(get_created_class)
        return True


class NoFieldRelationManager:
    """
    This class manages many to many relations for the model.
    It is accessible from the model attribute which does not have a many to many field.
    """
    def __init__(self, model_class, id) -> None:
        self.r_1 = model_class
        self.r_2 = self.get_relation()
        
        self.table_1 = self.r_1.__name__.lower()
        self.table_2 = self.r_2.__name__.lower()
        self.id = id
        self.junction_table = f'{self.table_1}_{self.table_2}'
        
    def get_relation(self):
        for relations in self.r_1.relation_tree.values():
            relation = [r for r in relations.values() if inspect.isclass(r) and r != self.r_1]
            return relation[0] if relation else None
 
    def all(self):
        rows = f', {self.table_2}.'.join(list(self.r_2.fields.keys())[:-1])
        query = ModelManagerQueries().no_field_manager_get_all(
            self.table_1, 
            self.table_2, 
            self.junction_table, 
            self.id, 
            rows
        )        
        return QuerySet(query, self.r_2).build()   
    
    
class QuerySet(QuerySetSearch):  
    """
    This method is used to hit the database and get the result.
    The result is returned in the form of a QuerySet object.
    The database is hit lazily meaning that the database is hit only
    when the __iter__ method is called or a filter method is called.
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
        for relation in RELATIONS:
            related_model = self.model_class.relation_tree.get(relation)
            if related_model:
                field_name = related_model.get('field_name')
               
                related_model = {f: c for f, c in list(related_model.items())[:1] if c != self.model_class}
                
                if field_name and related_model:                  
                    foreign_key_field, foreign_key_model = next(iter(related_model.items()))
                    return field_name, foreign_key_field, foreign_key_model
                    
        return False, False, False

    def build(self, get_unique=False) -> list: 
        if not self.cached_result:
            self.cached_result = self.query  
                  
        if get_unique:
            self.hit_db()
            return self.queryset[0] if self.queryset else None
        else:
            return self

    def hit_db(self):
        query = ExecuteQuery(self.cached_result).execute(read=True)
        relation_classes_without_relation_fields = get_relation_classes_without_relation_fields()
        
        if not query:
            return
        
        self.queryset = list()                                                                                 # Reset the queryset 

        for i, q in copy.copy(enumerate(query)):
            if len(self.model_class.fields.keys()) != len(query[i]):                                           # If the query result is a ManyToManyField, add the field which was deleted by the
                query[i] = q  + (RELATIONS[-1],)                                                               # BaseModel.certify_field_compatibility method.                                              
                
            obj_attrs = dict()
            additional_field = dict()
            
            field_name, foreign_key_field, foreign_key_model = self.check_for_relation()

            for key, value in zip(self.model_class.fields.keys(), query[i]):
                    
                if foreign_key_field and key == field_name:
                    if value == RELATIONS[-1]:                                                                  # Many To Many Relation
                        obj_attrs[key] = self.set_n_to_n_relation_manager(obj_attrs)
                    else:                                                                                       # One To One or Foreign Key Relation
                        obj_attrs[key] = foreign_key_model.objects.get(id=value)                                
                        
                elif self.model_class in relation_classes_without_relation_fields:                              # Relation without a field
                    
                    obj_attrs[key] = value 
                    
                    if next(iter(self.model_class.relation_tree)) == RELATIONS[-1]:                             # Many To Many Relation                                           
                        additional_field.update(
                            self.set_n_to_n_relation_manager_for_attr_without_field(obj_attrs))
                      
                else:
                    obj_attrs[key] = value                                                                      # Normal Field
                    
            if additional_field:
                obj_attrs = {**obj_attrs, **additional_field}       # If no field is present in the relation make sure to add it to the object attributes. 
                                                                    # Must be set at the end.
            self.queryset.append(self.model_class(**obj_attrs))
    
    
    def set_n_to_n_relation_manager(self, obj_attrs):
        r_tree = self.model_class.relation_tree.get(RELATIONS[-1])
        id = obj_attrs.get('id')
        r_2, r_1 = list(r_tree.keys())[:-1]
        return FieldRelationManager(id, r_1, r_2, r_tree)
    
    def set_n_to_n_relation_manager_for_attr_without_field(self, obj_attrs):                                                           
        relations = self.model_class.relation_tree.get(RELATIONS[-1])
        relation_model = [r for r in relations.values() if r != self.model_class][0]
        manager_name = f'{relation_model.__name__}_set'.lower()
        id = obj_attrs.get('id')
        return {manager_name: NoFieldRelationManager(self.model_class, id)}
    
                    
            