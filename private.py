import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint

import psycopg2
from flask import Flask, request, render_template, make_response, jsonify, abort

from post_modules.post import Post
from post_modules.collection import posts_collection

logger = logging.getLogger(__name__)
db = psycopg2.connect("dbname=thisisalsome user=thalida")
app = Flask(__name__)

# views
# - list of all posts (index)
# - view post (scrollable like public view, admin only @edit_button)
#     @edit_button => edit post view
# - create post
#     triggers an edit post view
# - edit post
#     1 post at a time
#     quill js magic


@app.route('/')
def list():
    return render_template('private/views/list.html')

@app.route('/read/{id}')
def read():
    return render_template('private/views/read.html')

@app.route('/edit/{id}')
def edit():
    return render_template('private/views/edit.html')


@app.route('/api/collection/posts', methods=['GET'])
def api_collection_list():
    try:
        # collection = posts_collection.get_all_latest_versions()
        collection = {}
        return make_response(jsonify(collection))
    except Exception:
        logger.exception('500 Error Getting all posts in a collection')
        abort(500)

@app.route('/api/post/upsert', methods=['POST'])
def api_post_upsert():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        post = posts_collection.get_or_create(post_id).save(api_json)
        posts_collection.store(post)
        return make_response(jsonify(post.latest_version.to_dict()))
    except Exception:
        logger.exception('500 Error Upserting Post')
        abort(500)

@app.route('/api/post/delete', methods=['POST'])
def api_post_delete():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        post = posts_collection.get_or_create(post_id).delete()
        posts_collection.store(post)
        return make_response(jsonify(post.latest_version.to_dict()))
    except Exception:
        logger.exception('500 Error Deleting Post')
        abort(500)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5002')
