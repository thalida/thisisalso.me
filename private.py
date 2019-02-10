import os
os.environ['TZ'] = 'UTC'

import logging
import psycopg2
import time
import datetime
from pprint import pprint
from flask import Flask, request, render_template, make_response, jsonify, abort

VERSION_AFTER_MINUTES = 5
ENABLED_STATUS_CODE = 1
DELETE_STATUS_CODE = 0 #in the  future more status codes could be added

# POST
# id
# create_time = DATETIME (w/o timezone)
# contents = TEXT
# theme = TEXT
# is_deleted = BOOLEAN



# API ENDPOINTS:
# /upsert
#       on save see if id passed in, try to create or update
# /create
#   creates a new primary key combo
#   if id => version
#   else => new post
# /update
#   updates a current post needs id
#   gets the newest create_time w/ that id
#   updates that id + create_time combo
# /delete
#   "soft delete"
#   TODO: ADD IS_DELETED FIELD
#   All posts w/ that id is marked as deleted



# TODOS:
# - Create psql helper lib
#       Move all functions to Post/Posts
#       Call helper class from api routes
# - Create Posts type class
# - Create Post Collection wrapper


logger = logging.getLogger(__name__)
db = psycopg2.connect("dbname=thisisalsome user=thalida")
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('private/index.html')

@app.route('/api/post/upsert', methods=['POST'])
def api_post_upsert():
    return upsert(request.get_json())

@app.route('/api/post/create', methods=['POST'])
def api_post_create():
    post_json = request.get_json()
    post_id = post_json.get('id')
    is_new_version = False if post_id is None else should_version(post_id)
    return create(post_json, is_version=is_new_version)

@app.route('/api/post/update', methods=['POST'])
def api_post_update():
    return update(request.get_json())

@app.route('/api/post/delete', methods=['POST'])
def api_post_delete():
    return delete(request.get_json())

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# get all data from last version and duplicate :shrug:
def get_newest_version_created_date(id):
    try:
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                sql_string= "SELECT created_date FROM post WHERE id=%s ORDER BY created_date DESC LIMIT 1;"
                cur.execute(sql_string, (id,))
                return cur.fetchone()[0]
    except Exception:
        logger.exception('Error getting recent version timestamp')

def xx_get_post_newest_version(id):
    try:
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                sql_string= "SELECT * FROM post WHERE id=%s ORDER BY created_date DESC LIMIT 1;"
                cur.execute(sql_string, (id,))
                return cur.fetchone()
    except Exception:
        logger.exception('Error getting recent version timestamp')


def should_version(id):
    try:
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                sql_string= "SELECT modified_date FROM post WHERE id=%s ORDER BY modified_date DESC LIMIT 1;"
                cur.execute(sql_string, (id,))
                post_update_tim = cur.fetchone()[0]
                now = datetime.datetime.now()
                elapsed_time = now - post_update_tim
                elapsed_min = int(int(elapsed_time.total_seconds()) / 60)
                return elapsed_min > VERSION_AFTER_MINUTES
        return False
    except Exception:
        logger.exception('Error getting should_version')


def upsert(post_json):
    try:
        post_id = post_json.get('id')
        is_new_version = False if post_id is None else should_version(post_id)
        if post_id is None or is_new_version:
            return create(post_json, is_version=is_new_version)
        else:
            return update(post_json)
    except Exception:
        logger.exception('500 Error Creating Post')
        abort(500)


def create(post_json, is_version=False):
    try:
        id = post_json.get('id', None)
        contents = post_json.get('contents', '')
        theme = post_json.get('theme')
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                if is_version:
                    sql_string = "INSERT INTO post (id, contents, theme) VALUES (%s, %s, %s) RETURNING id;"
                    data = (id, contents, theme,)
                else:
                    sql_string= "INSERT INTO post (contents, theme) VALUES (%s, %s) RETURNING id;"
                    data = (contents, theme,)

                cur.execute(sql_string, data)
                item = cur.fetchone()
                post_id = item[0]
        return make_response(jsonify({'status': 'success', 'id': post_id}))
    except Exception:
        logger.exception('500 Error Creating Post')
        abort(500)


def update(post_json):
    try:
        id = post_json.get('id', None)
        contents = post_json.get('contents', '')
        theme = post_json.get('theme')
        created_date = get_newest_version_created_date(id)
        print( '====', created_date)
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                sql_string= "UPDATE post SET contents=%s, theme=%s WHERE id=%s AND created_date=%s;"
                cur.execute(sql_string, (contents, theme, id, created_date,))
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Updating Post')
        abort(500)


def delete(post_json):
    try:
        id = post_json.get('id', None)
        with psycopg2.connect("dbname=thisisalsome user=thalida") as conn:
            with conn.cursor() as cur:
                sql_string= "UPDATE post SET status=%s WHERE id=%s;"
                cur.execute(sql_string, (DELETE_STATUS_CODE, id,))
        return make_response(jsonify({'status': 'success'}))
    except Exception:
        logger.exception('500 Error Updating Post')
        abort(500)


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5002')
