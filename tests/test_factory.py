# -*- coding: utf-8 -*-
"""
Tests for app factory
"""
from flaskr import create_app


def test_can_override_config() -> None:
    assert not create_app().testing

    assert create_app({"TESTING": True}).testing
