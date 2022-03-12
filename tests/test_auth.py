# -*- coding: utf-8 -*-
"""
Tests for auth-related code
"""
from http import HTTPStatus

import pytest
from faker import Faker
from flask import Flask, g, session
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from flaskr.models import User, db
from tests.conftest import AuthActions


def test_register_returns_registration_page(client: FlaskClient, app: Flask) -> None:
    response = client.get("/auth/register")

    assert response.status_code == HTTPStatus.OK

    assert b'value="Register"' in response.data


def test_successful_registration_creates_user_record(
    client: FlaskClient, app: Flask
) -> None:
    username = "a"

    response = client.post(
        "/auth/register", data={"username": username, "password": "a"}
    )

    assert "http://localhost/auth/login" == response.headers["Location"]

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        assert user is not None


@pytest.mark.parametrize(
    ("username", "password", "message", "create_user"),
    (
        ("", "", b"Username is required.", False),
        ("a", "", b"Password is required.", False),
        ("test", "test", b"already registered", True),
    ),
)
def test_register_validates_input(
    client: FlaskClient,
    app: Flask,
    username: str,
    password: str,
    message: bytes,
    create_user: bool,
):
    if create_user:
        with app.app_context():
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()

    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )

    assert message in response.data


def test_login_returns_login_form(client: FlaskClient) -> None:
    response = client.get("/auth/login")

    assert response.status_code == 200

    assert b'value="Log In"' in response.data


def test_can_login_successfully(
    client: FlaskClient, auth: AuthActions, app: Flask, faker: Faker
) -> None:
    username = faker.user_name()
    password = faker.password()

    with app.app_context():
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

    response = auth.login(username=user.username, password=password)

    assert response.headers["Location"] == "http://localhost/"

    with client:
        client.get("/")

        assert session["user_id"] == user.id

        assert g.user["username"] == user.username


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


def test_can_logout(
    client: FlaskClient, auth: AuthActions, faker: Faker, app: Flask
) -> None:
    username = faker.user_name()
    password = faker.password()

    with app.app_context():
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

    auth.login(username=user.username, password=password)

    with client:
        auth.logout()

        assert "user_id" not in session
