# -*- coding: utf-8 -*-
"""
Factories for models
"""
import factory
from werkzeug.security import generate_password_hash

from flaskr.models import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Factory for creating users.
    """

    class Meta:
        """
        Set necessary attributes for factory.
        """

        model = User

    id = factory.Sequence(lambda n: n)
    username = factory.Faker("user_name")
    password = factory.LazyAttribute(
        lambda u: generate_password_hash(u.password_plaintext)
    )

    class Params:
        password_plaintext = factory.Faker("password")
