import logging
import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from app import STATUS_CODES, VERSION_AFTER_MINUTES, DEFAULT_THEME, DEFAULT_STATUS

logger = logging.getLogger(__name__)

class PostModels(object):
    """docstring for PostModels"""
    def __init__(self, is_admin=False):
        super(PostModels, self).__init__()
        self.is_admin = is_admin

    def execute(self, fetch_action, query, query_args):
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, query_args)
                fetch_fn = getattr(cur, fetch_action)
                response = fetch_fn()

        return response

    def is_new_version(self, id=None, latest_version=None):
        if id is None or latest_version is None:
            return True

        try:
            now = datetime.datetime.now()
            elapsed_time = now - latest_version['last_modified_date']
            elapsed_min = int(elapsed_time.total_seconds() / 60)
            return elapsed_min > VERSION_AFTER_MINUTES
        except Exception:
            self.raise_error('Error figuring out if we need to version post {id}',
                            id=id)

    def fetch_all(self):
        try:
            posts = self.execute(
                'fetchall',
                """
                SELECT *
                FROM post as p1
                WHERE
                    status != %s
                AND p1.versioned_date = (
                    SELECT max(p2.versioned_date)
                    FROM post as p2
                    WHERE p2.id = p1.id
                )
                ORDER BY p1.last_modified_date DESC
                """,
                (STATUS_CODES['DELETED'],)
            )
            return posts
        except Exception:
            self.raise_error('PostModels: Error fetching all latest versions')
        pass


    def fetch_one(self, id, return_default=False):
        try:
            post = self.execute(
                'fetchone',
                """
                SELECT *
                FROM post as p1
                WHERE
                    id = %s
                AND status != %s
                ORDER BY versioned_date DESC
                LIMIT 1
                """,
                (id, STATUS_CODES['DELETED'],))

            if post is None and return_default:
                post = {
                    'id': None,
                    'contents': '',
                    'theme': DEFAULT_THEME,
                    'status': DEFAULT_STATUS,
                }

            return post
        except Exception:
            self.raise_error('Error fetching post with id: {id}', id=id)


        # get 1 post version by id
        pass

    def save(self, api_json):
        id = api_json.get('id', None)
        latest_version = self.fetch_one(id)
        if latest_version is not None:
            new_version_obj = {**latest_version, **api_json}
        else:
            new_version_obj = {**api_json}

        if self.is_new_version(id, latest_version):
            return self.create(id, new_version_obj)
        else:
            return self.update(id, new_version_obj)

    def create(self, id, new_version_obj):
        try:
            contents = new_version_obj.get('contents', '')
            theme = new_version_obj.get('theme', DEFAULT_THEME)
            status = new_version_obj.get('status', DEFAULT_STATUS)

            if id is None:
                query = """
                        INSERT INTO post (contents, theme, status)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """
                query_args = (contents, theme, status,)
            else:
                query = """
                        INSERT INTO post (id, contents, theme, status)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """
                query_args = (id, contents, theme, status,)

            post = self.execute('fetchone', query, query_args)
            return post
        except Exception:
            self.raise_error('Error inserting a new post: {post}',
                            post=new_version_obj)

    def update(self, id, new_version_obj):
        try:
            contents = new_version_obj.get('contents', '')
            theme = new_version_obj.get('theme', DEFAULT_THEME)
            status = new_version_obj.get('status')
            versioned_date = new_version_obj.get('versioned_date')

            query = """
                    UPDATE post SET contents=%s, theme=%s, status=%s
                    WHERE id=%s
                    AND versioned_date=%s
                    RETURNING *
                    """
            query_args = (contents, theme, status, id, versioned_date,)

            post = self.execute('fetchone', query, query_args)
            return post
        except Exception:
            self.raise_error('Error updating a post: {post}',
                            post=new_version_obj)

    def delete(self, api_json):
        try:
            id = api_json.get('id', None)
            query = "UPDATE post SET status=%s WHERE id=%s RETURNING *"
            query_args = (STATUS_CODES['DELETED'], id,)
            post = self.execute('fetchone', query, query_args)
            return post
        except Exception:
            self.raise_error('Error deleting a post: {id}', id=id)

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'spomething bad happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)


postModels = PostModels()
