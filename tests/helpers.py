# -*- coding: utf-8 -*-
"""
Helpers for tests
"""
from typing import Optional

from faker import Faker

from flaskr.models import User
from tests.factories import UserFactory


fake = Faker()


def create_user(
    username: Optional[str] = None, password: Optional[str] = None
) -> tuple[User, str]:
    """
    Creates a user to use in tests.

    Args:
        username (): Optional username
        password (): Optional password

    Returns:
        tuple containing the created user and their un-encrypted password.
    """
    username = username or fake.user_name()
    password = password or fake.password()

    user = UserFactory(username=username, password=password)

    return user, password
