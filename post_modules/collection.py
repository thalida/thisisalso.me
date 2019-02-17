import logging
from pprint import pprint

from collections import defaultdict

import psycopg2
from psycopg2.extras import RealDictCursor

from post_modules import STATUS_CODES, psql
from post_modules.post import Post

logger = logging.getLogger(__name__)

class Collection():
    """docstring for Collection"""
    def __init__(self):
        super(Collection, self).__init__()
        self.__collection = defaultdict()
        self.fetch()


    @property
    def collection(self):
        return self.__collection

    @collection.setter
    def collection(self, value):
        if not isinstance(value, dict):
            raise ValueError("Collection should be a dictionary")
        self.__collection = value

    def fetch(self):
        try:
            posts = psql.execute(
                'fetchall',
                "SELECT id FROM post WHERE status!=%s GROUP BY id;",
                (STATUS_CODES['DELETED'],)
            )
            for post in posts:
                self.get_or_create(post['id'], store_on_create=True)
            return self
        except Exception:
            logger.exception('Post: Error fetching all posts in collection')

    def get_post(self, id):
        return self.__collection.get(id, None)

    def get_all_latest_post_versions(self):
        dict = {post.id: post.latest_version.to_dict() for k, post in self.__collection.items()}
        return dict

    def get_post_lastest_version(self, id):
        post = self.get_post(id)
        return post.latest_version.to_dict()

    def get_post_versions(self, id):
        post = self.get_post(id)
        versions = {k: version.to_dict() for k, version in post.versions.items()}
        return versions

    def get_or_create(self, id, store_on_create=False):
        post = self.__collection.get(id, Post(id))

        if store_on_create is True:
            return self.store(post)
        else:
            return post

    def store(self, post):
        self.__collection[post.id] = post
        return self.__collection

    def remove(self, post_id):
        self.__collection.pop(post_id, None)

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'spomething bad happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
        raise Exception(msg)

collection = Collection()

