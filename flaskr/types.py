# -*- coding: utf-8 -*-
"""
Types for repo
"""
from typing import TypeAlias, Union

from flask import Response


ViewResponseType: TypeAlias = Union[str, Response]
