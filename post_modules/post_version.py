import logging
from pprint import pprint

import psycopg2
from psycopg2.extras import RealDictCursor

from post_modules import STATUS_CODES

logger = logging.getLogger(__name__)


class PostVersion():
    """docstring for PostVersion"""
    def __init__(self, id=None, versioned_date=None):
        super(PostVersion, self).__init__()
        self.id = id
        self.versioned_date = versioned_date
        self.status = None
        self.contents = None
        self.theme = None
        self.last_modified_date = None

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.get_status(),
            'contents': self.get_contents(),
            'theme': self.get_theme(),
            'versioned_date': self.get_versioned_date(),
            'last_modified_date': self.get_last_modified_date(),
        }

    def get_status(self):
        return self.status

    def get_contents(self):
        return self.contents

    def get_theme(self):
        return self.theme

    def get_versioned_date(self):
        return self.versioned_date

    def get_last_modified_date(self):
        return self.last_modified_date

    def set_all(self, db_json=None):
        if db_json is None:
            return

        for (field, value) in db_json.items():
            set_fn = getattr(self, 'set_{field}'.format(field=field))
            set_fn(value)

        return self

    def set_id(self, id):
        if self.id is not None and id != self.id:
            self.raise_error(
                'Post: Somehow fetched db post id {db_id} from post Class id {class_id}',
                db_id=db_json.get('id'),
                class_id=self.id
            )

        self.id = id
        return self.id

    def set_status(self, status):
        if status not in STATUS_CODES.values():
            self.raise_error(
                'Post: invalid status code of {status_code} provided',
                status_code=status
            )

        self.status = status
        return self.status

    def set_contents(self, contents):
        self.contents = contents
        return self.contents

    def set_theme(self, theme):
        self.theme = theme
        return self.theme

    def set_versioned_date(self, versioned_date):
        self.versioned_date = versioned_date
        return self.versioned_date

    def set_last_modified_date(self, last_modified_date):
        self.last_modified_date = last_modified_date
        return self.last_modified_date

    def raise_error(self, msg, **kwargs):
        msg = 'modules.post: bad things happended' if msg is None else msg
        msg = msg.format(**kwargs)
        logger.exception(msg)
        raise Exception(msg)

