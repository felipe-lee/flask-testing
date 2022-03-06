# -*- coding: utf-8 -*-
"""
Tests for blog functionality
"""
from http import HTTPStatus

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug import Response

from flaskr.db import get_db
from tests.conftest import AuthActions


def assert_post_is_in_response(response: Response, /) -> None:
    """
    Makes assertions about expected post.

    Args:
        response: response from request
    """
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data


def test_index_page_without_logging_in(client: FlaskClient, auth: AuthActions) -> None:
    response = client.get("/")

    # Should have links to log in and register
    assert b"Log In" in response.data
    assert b"Register" in response.data
    assert b"Log Out" not in response.data

    # Should see existing posts
    assert_post_is_in_response(response)

    # But should not be able to edit
    assert b"Edit" not in response.data

    # Should not be able to create new posts
    assert b"New" not in response.data


def test_index_page_as_logged_in_user(client: FlaskClient, auth: AuthActions) -> None:
    auth.login()

    response = client.get("/")

    # Should have a link to log out
    assert b"Log Out" in response.data
    assert b"Log In" not in response.data
    assert b"Register" not in response.data

    # Should see existing posts
    assert_post_is_in_response(response)

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


def test_author_required(app: Flask, client: FlaskClient, auth: AuthActions) -> None:
    # change the post author to another user
    with app.app_context():
        db = get_db()

        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")

        db.commit()

    auth.login()

    # current user can't modify other user's post
    assert client.post("/1/update").status_code == HTTPStatus.FORBIDDEN
    assert client.post("/1/delete").status_code == HTTPStatus.FORBIDDEN

    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize(
    "path",
    (
        "/2/update",
        "/2/delete",
    ),
)
def test_returns_proper_response_if_post_doesnt_exist(
    client: FlaskClient, auth: AuthActions, path: str
) -> None:
    auth.login()

    assert client.post(path).status_code == HTTPStatus.NOT_FOUND


def test_can_create_a_post(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()

    assert client.get("/create").status_code == HTTPStatus.OK

    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()

        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]

        assert count == 2


def test_can_update_a_post(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()

    assert client.get("/1/update").status_code == 200

    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()

        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()

        assert post["title"] == "updated"


@pytest.mark.parametrize(
    "path",
    (
        "/create",
        "/1/update",
    ),
)
def test_create_and_update_validate_posts(
    client: FlaskClient, auth: AuthActions, path: str
) -> None:
    auth.login()

    response = client.post(path, data={"title": "", "body": ""})

    assert b"Title is required." in response.data


def test_can_delete_a_post(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()

    response = client.post("/1/delete")

    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()

        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()

        assert post is None
