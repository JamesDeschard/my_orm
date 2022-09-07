from settings import DB_SETTINGS


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

    
class MigrationQueries:
    def create_table(self, table_name, fields):
        return f""" CREATE TABLE IF NOT EXISTS {table_name} 
                    (id {"INTEGER" if DB_SETTINGS.get("db_engine") == "sqlite3" else "SERIAL"} PRIMARY KEY,
                    {",".join(fields)});"""
    
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
        return f"SELECT * FROM {table_name}"

    
    
    
