from migrate import ExecuteQuery


class MigrationQueries:
    def create_table(self, table_name, fields):
        return f'CREATE TABLE {table_name} (id SERIAL PRIMARY KEY,{",".join(fields)});'
    
    def add_column(self, table_name, column_name, column_definition):
        return f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};'
    
    def remove_column(self, table_name, column_name):
        return f'ALTER TABLE {table_name} DROP COLUMN {column_name} ;'
        
    def drop_table(self, table_name):
        return f'DROP TABLE IF EXISTS {table_name};'
    

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
        return ExecuteQuery(query).execute(read=True)

    def create(self, table_name, column_name, value):
        query = f"""
                INSERT INTO {table_name} ({column_name})
                VALUES ({value})
                """
        return ExecuteQuery(query).execute()
    
    def update(self, table_name, id, **kwargs):
        query = f"UPDATE {table_name} SET "
        query = self.add_query_search_names_and_values(query, **kwargs, update=True)
        query += f" WHERE id = '{id}';"
        return ExecuteQuery(query).execute()
    
    def delete(self, table_name, **kwargs):
        query = f"DELETE FROM {table_name} WHERE "
        query = self.add_query_search_names_and_values(query, **kwargs)
        query = ExecuteQuery(query).execute()
    
    def get_all_columns(self, table_name):
        query = f"SELECT * FROM {table_name};"
        return ExecuteQuery(query).execute(read=True)


class QuerySet:
    def __init__(self, query, field_names, model_class) -> None:
        self.query = query
        self.field_names = field_names
        self.model_class = model_class
        self.queryset = list()
    
    def create(self) -> list:
        for q in self.query:
            obj_attrs = dict()
            for key, value in zip(['id'] + list(self.field_names), q):
                obj_attrs[key] = value
            self.queryset.append(self.model_class(**obj_attrs))
        if len(self.queryset) == 1:
            return self.queryset[0]
        return self.queryset
    
