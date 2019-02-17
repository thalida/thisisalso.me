import os
import re

import logging
from pprint import pprint

from flask import Blueprint, render_template, make_response, abort
from bs4 import BeautifulSoup

from app import AMDIN_ENV_KEY
from app.models import postModels

logger = logging.getLogger(__name__)
shared_routes = Blueprint(
    'shared_routes',
    __name__,
    template_folder='../views',
    static_folder='../views'
)

@shared_routes.route('/')
def view_index():
    try:
        posts = postModels.fetch_all()
        return render_template('list/list.html',
                                is_admin=os.getenv(AMDIN_ENV_KEY, False),
                                posts=posts)
    except Exception:
        logger.exception('')
        abort(404)

@shared_routes.route('/<int:post_id>')
def view_read(post_id):
    try:
        post = postModels.fetch_one(post_id)

        if post is None:
            abort(404)

        return render_template('read/read.html',
                                is_admin=os.getenv(AMDIN_ENV_KEY, False),
                                post_id=post_id,
                                post=post)
    except Exception:
        logger.exception('')
        abort(404)

@shared_routes.errorhandler(404)
def not_found(error):
    return make_response('', 404)



def html_excerpt(html, num_characters=100, append_string="…"):
    soup = BeautifulSoup(html, 'html5lib')
    full_text = soup.get_text()

    if len(full_text) <= num_characters:
        return soup.prettify()

    excerpt_text = list(full_text[:num_characters])
    escapted_excerpt = list(map(re.escape, excerpt_text))
    re_pattern = '((?:<.*?>)?' + '(?:<.*?>)?'.join(escapted_excerpt) + '(?:<.*?>)?)'
    m = re.search(re_pattern, html)

    excerpt_soup = BeautifulSoup(m.group(1).strip(), 'html5lib')
    last_el = excerpt_soup.find_all(string=re.compile('.+'))[-1].parent
    last_el.contents[-1].replace_with(last_el.contents[-1] + append_string)
    excerpt_html = excerpt_soup.prettify()
    return excerpt_html