# -*- coding: utf-8 -*-
"""
Code to handle blog and posts
"""
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
from sqlalchemy.orm import joinedload
from werkzeug import Response

from flaskr.auth import login_required
from flaskr.models import Post, db
from flaskr.types import ViewResponseType


bp = Blueprint("blog", __name__)


@bp.route("/")
def index() -> str:
    """
    Generates the template with the existing posts.

    Returns:
        index template.
    """
    posts = Post.query.options(joinedload("author"))

    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create() -> ViewResponseType:
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
            post = Post(
                author=g.user,
                title=title,
                body=body,
            )

            db.session.add(post)
            db.session.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:post_id>/update", methods=("GET", "POST"))
@login_required
def update(post_id: int) -> ViewResponseType:
    """
    Allows a user to edit a post.

    Returns:
        Either the post edit template (if first time through, or if there is invalid data in the
        form) or a redirect to the index page (if post edit is successful).
    """
    post = Post.query.options(joinedload("author")).get_or_404(post_id)

    if post.author.id != g.user.id:
        abort(403)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body

            db.session.add(post)
            db.session.commit()

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
    post = Post.query.get_or_404(post_id)

    if post.author_id != g.user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("blog.index"))
