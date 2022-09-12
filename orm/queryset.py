from .db_connections import ExecuteQuery


RELATIONS = ['ForeignKey', 'OneToOneField', 'ManyToManyField'] 


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
    
    
class RelationManager:    
    def __init__(self, id, r_1, r_2, r_tree) -> None:
        self.r_1_id = id
        self.r_1 = r_1
        self.r_2 = r_2
        self.r_tree = r_tree
        self.table_name = f'{self.r_1.lower()}_{self.r_2.lower()}'
        
    def add(self, *args):
        for obj in args:
            query = f"""INSERT INTO {self.table_name} 
                        ({self.r_1.lower()}_id, {self.r_2.lower()}_id) 
                        VALUES ({obj.id}, {self.r_1_id});"""
            ExecuteQuery(query).execute()

    def all(self):
        # Get all sutdents from student_class table
        relationship_class = self.r_tree.get(self.r_2)
        relationship_rows = f', {self.r_1.lower()}.'.join(relationship_class.fields.keys())
        
        query = f"""SELECT {self.r_1.lower()}.{relationship_rows} 
                    FROM {self.r_1.lower()} 
                    LEFT JOIN {self.table_name} ON {self.r_1.lower()}.id = {self.table_name}.{self.r_1.lower()}_id"""
        return QuerySet(query, relationship_class).build()

        
    
    def create(self, *args, **kwargs):
        pass
    
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
        if not query:
            return
        
        self.queryset = list()
        
        for i, q in enumerate(query):
            if len(self.model_class.fields.keys()) != len(query[0]):
                query[i] = q  + ('ManyToManyField',)

        for q in query:
            obj_attrs = dict()
            field_name, foreign_key_field, foreign_key_model = self.check_for_relation()

            for key, value in zip(self.model_class.fields.keys(), q):
                    
                if foreign_key_field and key == field_name:
                    if value == 'ManyToManyField':
                        r_tree = self.model_class.relation_tree.get('ManyToManyField')
                        id = obj_attrs.get('id')
                        r_2, r_1 = list(r_tree.keys())[:-1]
                        obj_attrs[key] = RelationManager(id, r_1, r_2, r_tree)
                    else:
                        obj_attrs[key] = foreign_key_model.objects.get(id=value)
                else:
                    obj_attrs[key] = value
                    
            self.queryset.append(self.model_class(**obj_attrs))
                    
            