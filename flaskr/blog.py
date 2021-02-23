""" Endpoints related to blogging functionality, e.g. viewing, creating, editing
    and deleting posts.
"""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


def get_post(post_id, check_author=True):
    """ Return post matching post id.
    param post_id: id# of post
    param check_author: if True, checks if user matches post author.
    """
    query = ('SELECT p.id, title, body, created, author_id, username'
             ' FROM post p JOIN user u ON p.author_id = u.id'
             ' WHERE p.id = ?')
    post = get_db().execute(query, (post_id,)).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(post_id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/')
def index():
    """ Index page showing list of posts """
    db = get_db()
    query = ('SELECT p.id, title, body, created, author_id, username'
             ' FROM post p JOIN user u ON p.author_id = u.id'
             ' ORDER BY created DESC')
    posts = db.execute(query).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """ GET:  display the post creation page
        POST: validate input and use input to create new post
    """
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO post (title, body, author_id)'
                       ' VALUES (?, ?, ?)', (title, body, g.user['id']))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:post_id>/update', methods=('GET', 'POST'))
@login_required
def update(post_id):
    """ GET:  display post edit page
        POST: validate and post the modified data
    """
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?',
                       (title, body, post_id))
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(post_id):
    """ POST: delete post from database """
    get_post(post_id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (post_id,))
    db.commit()
    return redirect(url_for('blog.index'))
