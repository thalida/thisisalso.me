import logging
from pprint import pprint

from collections import defaultdict

import psycopg2
from psycopg2.extras import RealDictCursor

from post_modules import STATUS_CODES
from post_modules.post import Post

logger = logging.getLogger(__name__)

class PostsCollection():
    """docstring for PostsCollection"""
    def __init__(self):
        super(PostsCollection, self).__init__()
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
            with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    sql_string = "SELECT id FROM post WHERE status!=%s GROUP BY id;"
                    data = (STATUS_CODES['DELETED'],)

                    cur.execute(sql_string, data)
                    posts = cur.fetchall()
                    for post in posts:
                        self.get_or_create(post['id'], store_on_create=True)
                    return self
        except Exception:
            logger.exception('Post: Error fetching all posts in collection')

    def find(self, id):
        return self.__collection.get(id, None)

    def get_or_create(self, id, store_on_create=False):
        post = self.__collection.get(id, Post(id))

        if store_on_create is True:
            return self.store(post)
        else:
            return post

    def store(self, post):
        self.__collection[post.id] = post
        return self.__collection

    @staticmethod
    def raise_error(msg, **kwargs):
        msg = 'modules.posts_collection: bad things happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
        raise Exception(msg)

    # def get_all_latest_versions(self):
    #     return {post.id: post.latest_version.to_dict() for k, post in self.__collection.items()}

    # def get_latest_version_for_post(self, id):
    #     post = self.find(id)
    #     return post.latest_version.to_dict() if post is not None else None

    # def get_all_versions(self):
    #     return {post_id: self.get_versions_for_post(post_id) for post_id in self.__collection.keys()}

    # def get_versions_for_post(self, id):
    #     post = self.find(id)
    #     return {
    #         post_version.versioned_date.isoformat(): post_version.to_dict()
    #         for k, post_version in post.version_collection.items()
    #     } if post is not None else None

posts_collection = PostsCollection()

