import os
os.environ['TZ'] = 'UTC'

import logging
import psycopg2
from pprint import pprint
from flask import Flask, request, render_template, make_response, jsonify, abort

# POST
# id = PK
# parent_id = FK
# contents = TEXT
# theme = TEXT
# timestamp = DATETIME (w/o timezone)
# (now() at time zone 'utc')

logger = logging.getLogger(__name__)
db = psycopg2.connect("dbname=thisisalsome user=thalida")
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('private/index.html')

@app.route('/api/post/create', methods=['POST'])
def api_create():
    try:
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO post (id, contents, theme) VALUES (%s, %s, %s)", (3, 'version testing one more time', '',))
                cur.execute("INSERT INTO post (contents, theme) VALUES (%s, %s)", ('foobarbatcat', '#ff4848',))
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Saving Post')
        abort(500)

@app.route('/api/post/save', methods=['POST'])
def api_save():
    try:
        bg_color = request.form.get('bg_color')
        html = request.form.get('html')
        print(bg_color, '     ', html)
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Saving Post')
        abort(500)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5002')
