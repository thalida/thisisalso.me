import psycopg2
from psycopg2.extras import RealDictCursor

VERSION_AFTER_MINUTES = 5
STATUS_CODES = {
    "DELETED": 0,
    "ENABLED": 1,
}
SUPPORTED_THEMES = {
    'Red': 'red',
    'Blue': '#0000ff',
}

class Psql(object):
    @staticmethod
    def execute(fetch_action, query, query_args):
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, query_args)
                fetch_fn = getattr(cur, fetch_action)
                response = fetch_fn()

        return response

psql = Psql()
