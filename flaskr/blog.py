# -*- coding: utf-8 -*-
"""
Code to handle blog and posts
"""
from typing import Any, Union

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug import Response

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint("blog", __name__)


@bp.route("/")
def index() -> str:
    """
    Generates the template with the existing posts.

    Returns:
        index template.
    """
    db = get_db()

    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()

    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create() -> Union[str, Response]:
    """
    Allows a user to create a post.

    Returns:
        Either the post creation template (if first time through, or if there is invalid data in the
        form) or a redirect to the index page (if post creation is successful).
    """
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()

            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


def get_post(
    post_id: int, /, *, check_author: bool = True
) -> Any:  # todo: not a great type hint...need to look at what can be done instead.
    """
    Grabs a post from the DB. Can optionally check if the post author matches the logged-in user
    (defaults to checking).

    Args:
        post_id (): ID of post to get from the DB.
        check_author (): Boolean indicating if this function should ensure the post author is the
            same as the logged-in user.

    Returns:
        The retrieved post.
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (post_id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:post_id>/update", methods=("GET", "POST"))
@login_required
def update(post_id: int) -> Union[str, Response]:
    """
    Allows a user to edit a post.

    Returns:
        Either the post edit template (if first time through, or if there is invalid data in the
        form) or a redirect to the index page (if post edit is successful).
    """
    post = get_post(post_id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()

            db.execute(
                "UPDATE post SET title = ?, body = ?" " WHERE id = ?",
                (title, body, post_id),
            )
            db.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:post_id>/delete", methods=("POST",))
@login_required
def delete(post_id: int) -> Response:
    """
    Allows a user to delete a post.

    Returns:
        Redirect to the index page.
    """
    get_post(post_id)

    db = get_db()

    db.execute("DELETE FROM post WHERE id = ?", (post_id,))
    db.commit()

    return redirect(url_for("blog.index"))
