import psycopg2

from fbaas.observable_proxy import unwrap
from fbaas.serializer import serialize

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"

class Storage:
    
    def update(self, state):
        """Update the state in the storage. For now it just replaces the whole state without any id (id = 0) or clever stuff."""
        
        print(f'Updating state in storage with {state}')
        
        query = """
        INSERT INTO state (id, data)
        VALUES (0, %s)
        ON CONFLICT (id) DO UPDATE
        SET data = EXCLUDED.data;
        """

        unwrapped = unwrap(state)
        
        print(f'Unwrapped state for storage: {unwrapped}')
        
        serialized = serialize(unwrapped)
        
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, [serialized])
        
    
    def create_database(self):
        """Creates the main table: state using the library of choice, psycopg2"""
    
        query_table = """
        CREATE TABLE IF NOT EXISTS state (
            id SERIAL PRIMARY KEY,
            data JSONB NOT NULL
        );
        """
        with psycopg2.connect(DATABASE_URL) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(query_table)

    def init(self):
        """Initializes the storage (database): creates the tables, etc."""
        self.create_database()
        print('Storage initialized')

    @classmethod
    def get_instance(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = cls()
        return cls.instance
