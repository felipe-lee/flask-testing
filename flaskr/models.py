# -*- coding: utf-8 -*-
"""
Database models for app
"""
from typing import TYPE_CHECKING

import click
from flask import Flask, current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()
BaseModel: DefaultMeta = db.Model


class User(BaseModel):
    """
    Site user
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    _password = db.Column("password", db.Text, nullable=False)

    @hybrid_property
    def password(self) -> str:
        """
        Return hashed password.

        Returns:
            hashed password
        """
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        """
        Hash and set password.

        Args:
            value: Value to hash and store as a password.
        """
        self._password = generate_password_hash(value)

    def check_password(self, value: str) -> bool:
        """
        Check password.

        Args:
            value: Password to compare to stored password.

        Returns:
            boolean indicating if the stored password matches the input password.
        """
        return check_password_hash(self._password, value)


class Post(BaseModel):
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
    Command to create new tables.
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
