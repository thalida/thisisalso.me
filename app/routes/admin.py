import logging
from pprint import pprint

from flask import Blueprint, request, render_template, make_response, jsonify, abort

from app.post.collection import collection

logger = logging.getLogger(__name__)
admin_routes = Blueprint(
    'admin_routes',
    __name__,
    template_folder='../views',
    static_folder='../views'
)

@admin_routes.route('/new')
@admin_routes.route('/<int:post_id>/edit')
def view_edit(post_id=None):
    try:
        post = collection.get_post_lastest_version(post_id) if post_id is not None else None
        return render_template('edit/edit.html', post_id=post_id, post=post)
    except Exception:
        logger.exception('Error viewing edit post')
        abort(404)

@admin_routes.route('/api/post/upsert', methods=['POST'])
def api_post_upsert():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        post = collection.get_or_create(post_id).save(api_json)
        collection.store(post)
        return make_response(jsonify(post.latest_version.to_dict()))
    except Exception:
        logger.exception('500 Error Upserting Post')
        abort(500)

@admin_routes.route('/api/post/delete', methods=['POST'])
def api_post_delete():
    try:
        api_json = request.get_json()
        post_id = api_json.get('id')
        post = collection.get_or_create(post_id).delete()
        collection.remove(post_id)
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Deleting Post')
        abort(500)
