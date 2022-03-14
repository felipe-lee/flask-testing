# -*- coding: utf-8 -*-
"""
Factories for models
"""
import factory
from factory.alchemy import SQLAlchemyModelFactory

from flaskr.models import User, db


class BaseFactory(SQLAlchemyModelFactory):
    """
    Base factory.
    """

    class Meta:
        """
        Factory configuration. Add session for all child factories
        """

        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
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
