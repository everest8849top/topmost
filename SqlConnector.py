from dotenv import load_dotenv, find_dotenv
import os
import psycopg2
from psycopg2 import extras

_ = load_dotenv(find_dotenv())

class SqlConnector:
    def __init__(self):
        self.connection_string = os.environ["TIMESCALE_CONNECTION_STRING"]
        pass

    def get_list_query_not_batch(self, query):
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)

        cur.execute(query)
        data = cur.fetchall()

        cur.close()
        conn.commit()
        conn.close()

        return data
