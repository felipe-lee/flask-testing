# -*- coding: utf-8 -*-
"""
Contains logic for opening and closing the DB connection
"""
import sqlite3
from sqlite3 import Connection
from typing import cast

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext


def get_db() -> Connection:
    """
    If a DB connection hasn't already been initialized into the global context, it will create a new
    connection and add it to the context.

    Returns:
        A connection to the DB.
    """
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None) -> None:
    """
    Removes the DB connection from the global context and closes it.
    Args:
        e (): I have no idea...the tutorial didn't say anything about this...
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db() -> None:
    """
    Gets a connection to the DB and then executes the schema file on the DB.
    """
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        file_contents = cast(bytes, f.read())

        db.executescript(file_contents.decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """
    Clear the existing data and create new tables.
    """
    init_db()

    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """
    Sets up the app to close the DB when tearing down, and adds the CLI command to initialize the
    DB.

    Args:
        app (): Flask app instance
    """
    app.teardown_appcontext(close_db)

    app.cli.add_command(init_db_command)
