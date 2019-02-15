import logging
from pprint import pprint

from operator import itemgetter
import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from post_modules import VERSION_AFTER_MINUTES, STATUS_CODES, psql
from post_modules.post_version import PostVersion

logger = logging.getLogger(__name__)

class Post():
    """docstring for Post"""
    def __init__(self, id):
        super(Post, self).__init__()
        self.id = id
        self.versions = {}
        self.latest_version = None

        if self.id is not None:
            self.fetch()

    def get_latest_version(self):
        return self.latest_version

    def set_latest_version(self):
        collection_items = self.versions.items()
        sorted_versions = sorted(collection_items,
                                key=itemgetter(0),
                                reverse=True)
        self.latest_version = sorted_versions[0][1]
        return self.latest_version

    def store(self, versions_json):
        if not isinstance(versions_json, (list, tuple,)):
            versions_json = [versions_json]

        if len(versions_json) == 0:
            return []

        for item in versions_json:
            versioned_date = item['versioned_date']
            post_version = self.versions.get(versioned_date, PostVersion())
            self.versions[versioned_date] = post_version.set_all(item)

        self.set_latest_version()
        return self.versions

    def fetch(self):
        if self.id is None:
            self.raise_error('Attempting to fetch a post with no id')

        try:
            res = psql.execute(
                            'fetchall',
                            "SELECT * FROM post WHERE id=%s;",
                            (self.id,))
            self.store(res)
            return self
        except Exception:
            self.raise_error('Error fetching post with id: {id}', id=self.id)

    def is_new_version(self):
        if self.id is None or self.latest_version is None:
            return True

        try:
            now = datetime.datetime.now()
            elapsed_time = now - self.latest_version.get_last_modified_date()
            elapsed_min = int(elapsed_time.total_seconds() / 60)
            return elapsed_min > VERSION_AFTER_MINUTES
        except Exception:
            self.raise_error('Error figuring out if we need to version post {id}',
                            id=self.id)

    def save(self, api_json):
        if self.latest_version is not None:
            new_version_obj = {**self.latest_version.to_dict(), **api_json}
        else:
            new_version_obj = {**api_json}

        if self.is_new_version():
            return self.create(new_version_obj)
        else:
            return self.update(new_version_obj)

    def create(self, new_version_obj):
        try:
            contents = new_version_obj.get('contents', '')
            theme = new_version_obj.get('theme', None)
            status = new_version_obj.get('status', STATUS_CODES['ENABLED'])

            if self.id is None:
                query = """
                        INSERT INTO post (contents, theme, status)
                        VALUES (%s, %s, %s) RETURNING *;
                        """
                query_args = (contents, theme, status,)
            else:
                query = """
                        INSERT INTO post (id, contents, theme, status)
                        VALUES (%s, %s, %s, %s) RETURNING *;
                        """
                query_args = (self.id, contents, theme, status,)

            res = psql.execute('fetchone', query, query_args)
            self.store(res)
            return self
        except Exception:
            self.raise_error('Error inserting a new post: {post}',
                            post=new_version_obj)

    def update(self, new_version_obj):
        try:
            contents = new_version_obj.get('contents', '')
            theme = new_version_obj.get('theme', None)
            status = new_version_obj.get('status')
            latest_versioned_date = self.latest_version.get_versioned_date()

            query = """
                    UPDATE post SET contents=%s, theme=%s, status=%s
                    WHERE id=%s
                    AND versioned_date=%s RETURNING *;
                    """
            query_args = (contents, theme, status, self.id, latest_versioned_date,)

            res = psql.execute('fetchone', query, query_args)
            self.store(res)
            return self
        except Exception:
            self.raise_error('Error updating a post: {post}',
                            post=new_version_obj)

    def delete(self):
        try:
            query = "UPDATE post SET status=%s WHERE id=%s RETURNING *;"
            query_args = (STATUS_CODES['DELETED'], self.id,)
            res = psql.execute('fetchone', query, query_args)
            self.store(res)
        except Exception:
            self.raise_error('Error deleting a post: {id}', id=self.id)

    def raise_error(self, msg, **kwargs):
        msg = 'modules.post: bad things happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
        raise Exception(msg)

