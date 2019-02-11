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
        self.collection = defaultdict()
        self.fetch()

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
        return self.collection.get(id, None)

    def get_or_create(self, id, store_on_create=False):
        post = self.collection.get(id, Post(id))

        if store_on_create is True:
            return self.store(post)
        else:
            return post

    def store(self, post):
        self.collection[post.id] = post
        return self.collection

    def raise_error(self, msg, **kwargs):
        msg = 'modules.posts_collection: bad things happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
        raise Exception(msg)

posts_collection = PostsCollection()

