# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present by Ehsan Maiqani.us
"""

from flask import Blueprint

blueprint = Blueprint(
    'base_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates',
    static_folder='static'
)
