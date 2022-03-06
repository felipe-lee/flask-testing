# -*- coding: utf-8 -*-
"""
Tests for auth-related code
"""
from http import HTTPStatus

import pytest
from flask import Flask, g, session
from flask.testing import FlaskClient

from flaskr.db import get_db
from tests.conftest import AuthActions


def test_register_returns_registration_page(client: FlaskClient, app: Flask) -> None:
    response = client.get("/auth/register")

    assert response.status_code == HTTPStatus.OK

    assert b'value="Register"' in response.data


def test_successful_registration_creates_user_record(
    client: FlaskClient, app: Flask
) -> None:
    response = client.post("/auth/register", data={"username": "a", "password": "a"})

    assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM user WHERE username = 'a'",
            )
            .fetchone()
            is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        ("test", "test", b"already registered"),
    ),
)
def test_register_validates_input(
    client: FlaskClient, username: str, password: str, message: bytes
):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )

    assert message in response.data


def test_login_returns_login_form(client: FlaskClient) -> None:
    response = client.get("/auth/login")

    assert response.status_code == 200

    assert b'value="Log In"' in response.data


def test_can_login_successfully(client: FlaskClient, auth: AuthActions) -> None:
    response = auth.login()

    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")

        assert session["user_id"] == 1

        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"Incorrect credentials."),
        ("test", "a", b"Incorrect credentials."),
    ),
)
def test_login_validates_input(
    auth: AuthActions, username: str, password: str, message: str
):
    response = auth.login(username, password)

    assert message in response.data


def test_can_logout(client: FlaskClient, auth: AuthActions) -> None:
    auth.login()

    with client:
        auth.logout()

        assert "user_id" not in session
