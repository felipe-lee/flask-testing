# -*- coding: utf-8 -*-
"""
Database models for app
"""
import click
from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """
    Site user
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)


class Post(db.Model):
    """
    User posts
    """

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = db.relationship("User", backref="posts", lazy=True)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP")
    )


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    """
    Clear the existing data and create new tables.
    """
    with current_app.app_context():
        db.create_all()

    click.echo("Initialized the database.")


def init_app(app: Flask) -> None:
    """
    Sets up the app to close the DB when tearing down, and adds the CLI command to initialize the
    DB.

    Args:
        app (): Flask app instance
    """
    db.init_app(app)

    app.cli.add_command(init_db_command)
