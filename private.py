import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint

import datetime
import json

from flask import Flask
from flask_socketio import SocketIO, emit

from app.routes.shared import shared_routes, html_excerpt
from app.models import postModels

logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder = './app/views')
app.url_map.strict_slashes = False
app.jinja_env.filters['html_excerpt'] = html_excerpt
app.register_blueprint(shared_routes)
socketio = SocketIO(app)

def to_json(obj):
    return json.dumps(
        obj,
        default=lambda o: o.isoformat() if isinstance(o, datetime.datetime) else o
    )


@app.route('/new')
@app.route('/<int:post_id>/edit')
def view_edit(post_id=None):
    try:
        post = postModels.fetch_one(post_id)
        return render_template('edit/edit.html', post_id=post_id, post=post)
    except Exception:
        logger.exception('Error viewing edit post')
        abort(404)

@socketio.on('save')
def handle_save(json_req):
    try:
        post = to_json(postModels.save(json_req))
        emit('post_update', post, broadcast=True)
        return post
    except Exception:
        logger.exception('500 Error Saving Post')

@socketio.on('delete')
def handle_save(json_req):
    try:
        post = to_json(postModels.delete(json_req))
        emit('post_update', post, broadcast=True)
        return post
    except Exception:
        logger.exception('500 Error Saving Post')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True, host='0.0.0.0', port='5002')
    socketio.run(app, debug=True, host='0.0.0.0', port='5002')
