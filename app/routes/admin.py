import logging
from pprint import pprint

from flask import Blueprint, request, render_template, make_response, jsonify, abort

from app.models import postModels

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
        post = postModels.fetch_one(post_id)
        return render_template('edit/edit.html', post_id=post_id, post=post)
    except Exception:
        logger.exception('Error viewing edit post')
        abort(404)

@admin_routes.route('/api/post/upsert', methods=['POST'])
def api_post_upsert():
    try:
        post = postModels.save(request.get_json())
        return make_response(jsonify(post))
    except Exception:
        logger.exception('500 Error Upserting Post')
        abort(500)

@admin_routes.route('/api/post/delete', methods=['POST'])
def api_post_delete():
    try:
        post = postModels.save(request.get_json())
        return make_response(jsonify({'status': 'success', 'post': post}))
    except Exception:
        logger.exception('500 Error Deleting Post')
        abort(500)
