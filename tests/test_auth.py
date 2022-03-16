# -*- coding: utf-8 -*-
"""
Tests for auth-related code
"""
from http import HTTPStatus

import pytest
from faker import Faker
from flask import Flask, g, session
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from flaskr.models import User
from tests.conftest import AuthActions
from tests.factories import UserFactory


def test_register_returns_registration_page(client: FlaskClient, app: Flask) -> None:
    response = client.get("/auth/register")

    assert response.status_code == HTTPStatus.OK

    assert b'value="Register"' in response.data


def test_successful_registration_creates_user_record(
    client: FlaskClient, app: Flask, db: SQLAlchemy
) -> None:
    username = "a"

    response = client.post(
        "/auth/register", data={"username": username, "password": "a"}
    )

    assert "http://localhost/auth/login" == response.headers["Location"]

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
    db: SQLAlchemy,
    username: str,
    password: str,
    message: bytes,
    create_user: bool,
) -> None:
    if create_user:
        with app.app_context():
            user = User(username=username, password=password)

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
    client: FlaskClient,
    auth: AuthActions,
    app: Flask,
    faker: Faker,
    db: SQLAlchemy,
) -> None:
    password = faker.password()

    user = UserFactory(password=password)

    response = auth.login(username=user.username, password=password)

    assert response.headers["Location"] == "http://localhost/"

    client.get("/")

    assert session["user_id"] == user.id

    assert g.user.username == user.username


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", b"Incorrect credentials."),
        ("test", "a", b"Incorrect credentials."),
    ),
)
def test_login_validates_input(
    auth: AuthActions, username: str, password: str, message: str, db: SQLAlchemy
) -> None:
    response = auth.login(username, password)

    assert message in response.data


def test_can_logout(
    client: FlaskClient,
    auth: AuthActions,
    faker: Faker,
    app: Flask,
    db: SQLAlchemy,
) -> None:
    password = faker.password()

    user = UserFactory(password=password)

    auth.login(username=user.username, password=password)

    auth.logout()

    assert "user_id" not in session
