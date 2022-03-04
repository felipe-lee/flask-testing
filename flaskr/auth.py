# -*- coding: utf-8 -*-
"""
Code to handle auth in the project
"""
import functools
from typing import Any, Callable, TypeVar, Union, cast

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug import Response
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register() -> Union[str, Response]:
    """
    Allows a user to register for the website.

    Returns:
        Either the registration template (if first time through, or if there is invalid data in the
        form) or a redirect to the login page (if registration is successful).
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login() -> Union[str, Response]:
    """
    Allows a user to log in to the website.

    Returns:
        Either the login template (if first time through, or if there is invalid data in the
        form) or a redirect to the index page (if login is successful).
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        error = None

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect credentials."

        if error is None:
            session.clear()

            session["user_id"] = user["id"]

            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user() -> None:
    """
    Grabs the user ID from the session and attempts to load the user into the global context.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/logout")
def logout() -> Response:
    """
    Clears the user's session and redirects to the index.

    Returns:
        Redirect to the index page.
    """
    session.clear()

    return redirect(url_for("index"))


F = TypeVar("F", bound=Callable[..., Any])


def login_required(view: F) -> F:
    """
    Decorator that view functions can use to ensure the user is logged in before regular view logic
    runs.

    Args:
        view (): Function to decorate.

    Returns:
        Decorated function
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """
        Checks if the user is logged in. If so, calls view with kwargs, otherwise, redirects to the
        login page.

        Args:
            **kwargs (): kwargs for view.

        Returns:
            Either the return value of the wrapped view, or a redirect to the login page.
        """
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return cast(F, wrapped_view)
