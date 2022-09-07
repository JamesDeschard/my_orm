from migrate import ExecuteQuery

class QuerySetSearch:
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
    

class QuerySet(QuerySetSearch):
    def __init__(self, query, model_class) -> None:
        super().__init__(str())
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
                foreignkey = __import__('models')
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
            
