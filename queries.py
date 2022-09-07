class DbStatusQueries:
    def table_exists_query(self, table_name):
        return f""" SELECT EXISTS (SELECT table_name FROM information_schema.tables 
                    WHERE table_name = '{table_name}'); """
    
    def get_all_tables_query(self):
        return """ SELECT table_name FROM information_schema.tables
                                WHERE table_schema = 'public'; """
    
    def get_table_columns_query(self, table_name):
        return f""" SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{table_name}'; """

    
class MigrationQueries:
    def create_table(self, table_name, fields):
        return f'CREATE TABLE {table_name} (id SERIAL PRIMARY KEY,{",".join(fields)});'
    
    def add_column(self, table_name, column_name, column_definition):
        return f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};'
    
    def remove_column(self, table_name, column_name):
        return f'ALTER TABLE {table_name} DROP COLUMN {column_name} ;'
        
    def drop_table(self, table_name):
        return f'DROP TABLE IF EXISTS {table_name} CASCADE;'
    

class ModelManagerQueries:
    def add_query_search_names_and_values(self, query, update=False, **kwargs):
        for index, (key, value) in enumerate(kwargs.items()):
            query += f"{key} = '{value}'"
            kwargs_length_minus_1 = len(kwargs.items()) - 1
            if index < kwargs_length_minus_1:
                if update:
                    query += ', '
                else:
                    query += ' AND '
        return query
    
    def get(self, table_name, **kwargs):
        query = f"SELECT * FROM {table_name} WHERE "
        query = self.add_query_search_names_and_values(query, **kwargs)
        return query

    def create(self, table_name, column_name, value):
        query = f"""
                INSERT INTO {table_name} ({column_name})
                VALUES ({value})
                """
        return query
    
    def update(self, table_name, id, **kwargs):
        query = f"UPDATE {table_name} SET "
        query = self.add_query_search_names_and_values(query, **kwargs, update=True)
        query += f" WHERE id = '{id}';"
        return query
    
    def delete(self, table_name, **kwargs):
        query = f"DELETE FROM {table_name} WHERE "
        query = self.add_query_search_names_and_values(query, **kwargs)
        return query
    
    def get_all_columns(self, table_name):
        return f"SELECT * FROM {table_name};"


class QueryObject:
    def __init__(self) -> None:
        pass


class QuerySet:
    def __init__(self, query, model_class) -> None:
        self.query = query
        self.model_class = model_class
        self.queryset = list()
        self.index = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.queryset):
            result = self.queryset[self.index]
            self.index += 1
            return result
        raise StopIteration
    
    def __len__(self):
        return len(self.queryset)
        
    def check_for_relation(self):
        for field_name, field_value in self.model_class.fields.items():
            if field_value.__class__.__name__ == 'ForeignKey':
                foreignkey = __import__('models')
                foreignkey = getattr(foreignkey, field_name.capitalize())
                return field_name, foreignkey
        return False, False


    def create(self) -> list:
        for q in self.query:
            
            obj_attrs = dict()
            foreign_key_field, foreign_key_model = self.check_for_relation()
            
            for key, value in zip(self.model_class.fields.keys(), q):
                if foreign_key_field and key == foreign_key_field:
                    obj_attrs[key] = foreign_key_model.objects.get(id=value)
                else:
                    obj_attrs[key] = value
                    
            self.queryset.append(self.model_class(**obj_attrs))
        if len(self.queryset) == 1:
            return self.queryset[0]
        return self
    
    def filter(self, **kwargs):
        return 'Filter method called'
    
    def first(self):
        pass
    
    
    
