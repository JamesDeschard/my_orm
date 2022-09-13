import copy
import inspect

from .db_connections import ExecuteQuery
from .utils import get_relation_classes_without_relation_fields, relations

RELATIONS = relations()


class QuerySetSearch:
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
    
    
class FieldRelationManager:    
    def __init__(self, id, r_1, r_2, r_tree) -> None:
        self.r_1_id = id
        self.r_1 = r_1
        self.r_2 = r_2
        
        self.relation_class = r_tree.get(self.r_2)
        self.table_name = f'{self.r_1.lower()}_{self.r_2.lower()}'
    
    def insertion_query(self, obj):
        return f""" INSERT INTO {self.table_name} ({self.r_1.lower()}_id, {self.r_2.lower()}_id) 
                    VALUES ({obj.id}, {self.r_1_id});"""
    
    def add(self, *args):
        return list(map(lambda q: ExecuteQuery(self.insertion_query(q)).execute(), args))

    def all(self):
        relationship_rows = f', {self.r_1.lower()}.'.join(self.relation_class.fields.keys())
        
        query = f"""SELECT {self.r_1.lower()}.{relationship_rows} 
                    FROM {self.table_name}
                    INNER JOIN {self.r_1.lower()} ON {self.r_1.lower()}.id = {self.table_name}.{self.r_1.lower()}_id
                    WHERE {self.table_name}.{self.r_2.lower()}_id = {self.r_1_id};"""    
        return QuerySet(query, self.relation_class).build()

    def create(self, **kwargs):
        self.relation_class.objects.create(**kwargs)
        get_created_class = self.relation_class.objects.get(**kwargs)
        self.add(get_created_class)
        return True


class NoFieldRelationManager:
    def __init__(self, model_class, id) -> None:
        self.r_1 = model_class
        self.r_2 = self.get_relations()
        self.id = id
        self.table_name = f'{self.r_1.__name__.lower()}_{self.r_2.__name__.lower()}'
        
    def get_relations(self):
        for relations in self.r_1.relation_tree.values():
            for relation in relations.values():
                if inspect.isclass(relation) and relation != self.r_1:
                    return relation
 
    def all(self):
        relationship_rows = f', {self.r_2.__name__.lower()}.'.join(list(self.r_2.fields.keys())[:-1])
        
        query = f"""SELECT {self.r_2.__name__.lower()}.{relationship_rows} 
                    FROM {self.table_name}
                    INNER JOIN {self.r_2.__name__.lower()} ON {self.r_2.__name__.lower()}.id = {self.table_name}.{self.r_2.__name__.lower()}_id
                    WHERE {self.table_name}.{self.r_1.__name__.lower()}_id = {self.id};"""
        
        return QuerySet(query, self.r_2).build()   
    
    
class QuerySet(QuerySetSearch):  

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
        
        self.queryset = list()

        for i, q in copy.copy(enumerate(query)):
            if len(self.model_class.fields.keys()) != len(query[i]):
                query[i] = q  + (RELATIONS[-1],)
                
            obj_attrs = dict()
            additional_field = dict()
            
            field_name, foreign_key_field, foreign_key_model = self.check_for_relation()

            for key, value in zip(self.model_class.fields.keys(), query[i]):
                    
                if foreign_key_field and key == field_name:
                    if value == RELATIONS[-1]:
                        r_tree = self.model_class.relation_tree.get(RELATIONS[-1])
                        id = obj_attrs.get('id')
                        r_2, r_1 = list(r_tree.keys())[:-1]
                        obj_attrs[key] = FieldRelationManager(id, r_1, r_2, r_tree)
                    else:
                        obj_attrs[key] = foreign_key_model.objects.get(id=value)  
                        
                elif self.model_class in relation_classes_without_relation_fields: 
                    
                    obj_attrs[key] = value 
                    is_many_to_many = next(iter(self.model_class.relation_tree)) == RELATIONS[-1]
                    
                    if not additional_field and is_many_to_many:
                        relations = self.model_class.relation_tree.get(RELATIONS[-1])
                        # This third loop never has a length > 2
                        for _class in list(relations.values())[:-1]:
                            if _class not in relation_classes_without_relation_fields:
                                manager_name = _class.__name__.lower() + '_set'
                                if not additional_field.get(manager_name):
                                    id = obj_attrs.get('id')
                                    additional_field[manager_name] = NoFieldRelationManager(self.model_class, id)
                    
                else:
                    obj_attrs[key] = value
                    
            if additional_field:
                obj_attrs = {**obj_attrs, **additional_field}
                
            self.queryset.append(self.model_class(**obj_attrs))
                    
            