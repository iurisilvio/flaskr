# imports
from flask import Flask, request, session, redirect, url_for, \
    abort, render_template, flash, jsonify
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
import os

# grabs the folder where the script runs
basedir = os.path.abspath(os.path.dirname(__file__))

# configuration
DATABASE = 'flaskr.db'
DEBUG = True
SECRET_KEY = 'my_precious'
USERNAME = 'admin'
PASSWORD = 'admin'

# defines the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                         'sqlite:///' + DATABASE_PATH)
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'null')

# create app
app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
cache = Cache(app)

import models


@app.route('/')
@app.route('/<int:last_post_id>')
@cache.cached(timeout=5)
def index(last_post_id=None):
    """Searches the database for entries, then displays them."""
    q = db.session.query(models.Flaskr)
    if last_post_id is not None:
        q.filter(models.Flaskr.post_id < last_post_id)
    entries = q.order_by(models.Flaskr.post_id.desc()).limit(20)
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Adds new post to the database."""
    if not session.get('logged_in'):
        abort(401)
    new_entry = models.Flaskr(request.form['title'], request.form['text'])
    db.session.add(new_entry)
    db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))


@app.route('/delete/<int:post_id>', methods=['GET'])
def delete_entry(post_id):
    """Deletes post from database"""
    result = {'status': 0, 'message': 'Error'}
    try:
        new_id = post_id
        db.session.query(models.Flaskr).filter_by(post_id=new_id).delete()
        db.session.commit()
        result = {'status': 1, 'message': "Post Deleted"}
        flash('The entry was deleted.')
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)

if __name__ == '__main__':
    app.run()
