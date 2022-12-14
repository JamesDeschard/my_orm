from settings import DB_SETTINGS

    
class MigrationQueries:
    def engine_type_var(self, engine, option_1, option_2):
        return option_1 if DB_SETTINGS.get("db_engine") == engine else option_2
    
    def create_table(self, table_name, fields):
        return f""" CREATE TABLE IF NOT EXISTS {table_name} 
                    (id {self.engine_type_var('sqlite3', 'INTEGER', 'SERIAL')} PRIMARY KEY,
                    {", ".join(fields)});"""
    
    def add_column(self, table_name, column_name, column_definition):
        return f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};'
    
    def remove_column(self, table_name, column_name):
        return f'ALTER TABLE {table_name} DROP COLUMN {column_name} ;'
        
    def drop_table(self, table_name):
        return f'DROP TABLE IF EXISTS {table_name} {self.engine_type_var("sqlite3", "", "CASCADE")};'
    

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
        return f'INSERT INTO {table_name} ({column_name})VALUES ({value})'

    
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
        return f"SELECT * FROM {table_name}"
    
    def no_field_manager_get_all(self, table_1, table_2, junction_table, id, rows):
        return f""" SELECT {table_2}.{rows} 
                    FROM {junction_table}
                    INNER JOIN {table_2} ON {table_2}.id = {junction_table}.{table_2}_id
                    WHERE {junction_table}.{table_1}_id = {id};"""
    
    def field_manager_add(self, junction_table, table_1, table_2, id_1, id_2):
        return f""" INSERT INTO {junction_table} ({table_1}_id, {table_2}_id) 
                    VALUES ({id_1}, {id_2});"""
    
    def field_manager_all(self, junction_table, table_1, table_2, id, rows):
        return f""" SELECT {table_1}.{rows} 
                    FROM {junction_table}
                    INNER JOIN {table_1} ON {table_1}.id = {junction_table}.{table_1}_id
                    WHERE {junction_table}.{table_2}_id = {id};""" 


class DbStatusQueriesPostgres:
    def table_exists_query(self, table_name):
        return f""" SELECT EXISTS (SELECT table_name FROM information_schema.tables 
                    WHERE table_name = '{table_name}'); """
    
    def get_all_tables_query(self):
        return """ SELECT table_name FROM information_schema.tables
                                WHERE table_schema = 'public'; """
    
    def get_table_columns_query(self, table_name):
        return f""" SELECT column_name FROM information_schema.columns
                    WHERE table_name = '{table_name}'; """


class DbStatusQueriesSqlite:
    def table_exists_query(self, table_name):
        return f""" SELECT name FROM sqlite_schema WHERE type='table' AND name='{table_name}'; """
    
    def get_all_tables_query(self):
        return """ SELECT name FROM sqlite_schema WHERE type='table'; """
    
    def get_table_columns_query(self, table_name):
        return f""" PRAGMA table_info({table_name})"""
            