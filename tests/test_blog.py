# -*- coding: utf-8 -*-
"""
Tests for blog functionality
"""
from http import HTTPStatus

import pytest
from faker import Faker
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Response

from flaskr.models import Post
from tests.conftest import AuthActions
from tests.helpers import create_user


def assert_post_is_in_response(post: Post, response: Response, /) -> None:
    """
    Makes assertions about expected post.

    Args:
        post: post to check for
        response: response from request
    """
    assert post.title.encode() in response.data

    post_details = f'by {post.author.username} on {post.created.strftime("%Y-%m-%d")}'

    assert post_details.encode() in response.data

    assert post.body.encode() in response.data


def test_index_page_without_logging_in(
    faker: Faker, client: FlaskClient, db: SQLAlchemy
) -> None:
    user, _ = create_user()

    post = Post(title=faker.sentence(), body=faker.paragraph(), author=user)

    db.session.add(post)
    db.session.commit()

    response = client.get("/")

    # Should have links to log in and register
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Log Out" not in response.data

    # Should see existing posts
    assert_post_is_in_response(post, response)

    # But should not be able to edit
    assert b"Edit" not in response.data

    # Should not be able to create new posts
    assert b"New" not in response.data


def test_index_page_as_logged_in_user(
    faker: Faker, client: FlaskClient, db: SQLAlchemy, auth: AuthActions
) -> None:
    user, password = create_user()

    post = Post(title=faker.sentence(), body=faker.paragraph(), author=user)

    db.session.add(post)
    db.session.commit()

    auth.login(username=user.username, password=password)

    response = client.get("/")

    # Should have a link to log out
    assert b"Log Out" in response.data
    assert b"Log In" not in response.data
    assert b"Register" not in response.data

    # Should see existing posts
    assert_post_is_in_response(post, response)

    # Should be able to edit
    assert b"Edit" in response.data
    assert b'href="/1/update"' in response.data

    # Should also be able to create new posts
    assert b"New" in response.data


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
        "/1/delete",
    ),
)
def test_login_required(client: FlaskClient, path: str) -> None:
    response = client.post(path)

    assert response.status_code == HTTPStatus.FOUND

    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(
    faker: Faker, client: FlaskClient, db: SQLAlchemy, app: Flask, auth: AuthActions
) -> None:
    author, _ = create_user()

    post = Post(title=faker.sentence(), body=faker.paragraph(), author=author)

    db.session.add(post)
    db.session.commit()

    user, password = create_user()

    auth.login(username=user.username, password=password)

    # current user can't modify other user's post
    assert client.post("/1/update").status_code == HTTPStatus.FORBIDDEN
    assert client.post("/1/delete").status_code == HTTPStatus.FORBIDDEN

    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize(
    "path",
    (
        "/1/update",
        "/1/delete",
    ),
)
def test_returns_proper_response_if_post_doesnt_exist(
    faker: Faker, client: FlaskClient, auth: AuthActions, db: SQLAlchemy, path: str
) -> None:
    user, password = create_user()

    auth.login(username=user.username, password=password)

    assert client.post(path).status_code == HTTPStatus.NOT_FOUND


def test_can_create_a_post(
    faker: Faker, db: SQLAlchemy, client: FlaskClient, auth: AuthActions, app: Flask
) -> None:
    user, password = create_user()

    auth.login(username=user.username, password=password)

    assert client.get("/create").status_code == HTTPStatus.OK

    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        count = Post.query.count()

        assert count == 1


def test_can_update_a_post(
    faker: Faker, db: SQLAlchemy, client: FlaskClient, auth: AuthActions, app: Flask
) -> None:
    user, password = create_user()

    original_title = faker.sentence()

    post = Post(title=original_title, body=faker.paragraph(), author=user)

    db.session.add(post)
    db.session.commit()

    auth.login(username=user.username, password=password)

    assert client.get("/1/update").status_code == 200

    while (new_title := faker.sentence()) == original_title:
        continue

    client.post("/1/update", data={"title": new_title, "body": ""})

    with app.app_context():
        post = Post.query.get(1)

        assert post.title != original_title
        assert post.title == new_title


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_and_update_validate_posts(
    faker: Faker, db: SQLAlchemy, client: FlaskClient, auth: AuthActions, path: str
) -> None:
    user, password = create_user()

    post = Post(title=faker.sentence(), body=faker.paragraph(), author=user)

    db.session.add(post)
    db.session.commit()

    auth.login(username=user.username, password=password)

    response = client.post(path, data={"title": "", "body": ""})

    assert b"Title is required." in response.data


def test_can_delete_a_post(
    faker: Faker, db: SQLAlchemy, client: FlaskClient, auth: AuthActions, app: Flask
) -> None:
    user, password = create_user()

    post = Post(title=faker.sentence(), body=faker.paragraph(), author=user)

    db.session.add(post)
    db.session.commit()

    auth.login(username=user.username, password=password)

    response = client.post("/1/delete")

    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        post = Post.query.get(1)

        assert post is None
