import psycopg2
from psycopg2.extras import DictCursor


def get_connection():
    return psycopg2.connect(user="postgres", password="1234", host="localhost",
                            port="5432", database="postgres", cursor_factory=DictCursor)
