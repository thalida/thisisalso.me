import os
os.environ['TZ'] = 'UTC'

import logging
from pprint import pprint

from flask import Flask

from app.routes.shared import shared_routes, html_excerpt

logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder = './app/views')
app.url_map.strict_slashes = False
app.jinja_env.filters['html_excerpt'] = html_excerpt
app.register_blueprint(shared_routes)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5001')
