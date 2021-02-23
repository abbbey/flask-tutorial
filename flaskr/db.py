""" Methods for accessing post/user tables in the database """
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


# sql commands to initialize fresh db
INIT_DB_SQL='schema.sql'


def get_db():
    """ Return a connection to the database """
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """ Close the database connection """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """ Initialize the database using schema.sql """
    db = get_db()

    with current_app.open_resource(INIT_DB_SQL) as fptr:
        db.executescript(fptr.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """ Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """ Register db-related hooks to the app """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
