import os
os.environ['TZ'] = 'UTC'

import re
import logging
from pprint import pprint

from flask import Flask, request, render_template, make_response, jsonify, abort, Markup
from bs4 import BeautifulSoup

from post_modules.post import Post
from post_modules.collection import collection

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.url_map.strict_slashes = False

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

app.jinja_env.filters['html_excerpt'] = html_excerpt

@app.route('/')
def view__index():
    try:
        posts = collection.get_all_latest_post_versions()
        sorted_posts = sorted(posts.items(),
                                key=lambda p: p[1]['last_modified_date'],
                                reverse=True)
        sorted_posts_dict = {x: y for x, y in sorted_posts}
        return render_template('views/list.html', posts=sorted_posts_dict)
    except Exception:
        abort(404)

@app.route('/<int:post_id>')
def view__post_read(post_id):
    try:
        post = collection.get_post_lastest_version(post_id)
        return render_template('views/read.html', post_id=post_id, post=post)
    except Exception:
        abort(404)

@app.route('/new')
@app.route('/<int:post_id>/edit')
def view__post_edit(post_id=None):
    try:
        post = collection.get_post_lastest_version(post_id) if post_id is not None else None
        return render_template('views/edit.html', post_id=post_id, post=post)
    except Exception:
        abort(404)


@app.route('/api/collection/posts', methods=['GET'])
def api__collection_list():
    try:
        # collection = collection.get_all_latest_versions()
        collection = {}
        return make_response(jsonify(collection))
    except Exception:
        logger.exception('500 Error Getting all posts in a collection')
        abort(500)

@app.route('/api/post/upsert', methods=['POST'])
def api__post_upsert():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        print(post_id)
        post = collection.get_or_create(post_id).save(api_json)
        collection.store(post)
        return make_response(jsonify(post.latest_version.to_dict()))
    except Exception:
        logger.exception('500 Error Upserting Post')
        abort(500)

@app.route('/api/post/delete', methods=['POST'])
def api__post_delete():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        post = collection.get_or_create(post_id).delete()
        collection.remove(post_id)
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Deleting Post')
        abort(500)

@app.errorhandler(404)
def not_found(error):
    return make_response('', 404)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5002')
