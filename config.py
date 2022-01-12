# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present by Ehsan Maiqani
"""

import os
from   os import environ

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    SECRET_KEY = 'key'

    # This will create a file in <app> FOLDER
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')

    # Mysql database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        environ.get('APPSEED_DATABASE_USER', 'root'),
        environ.get('APPSEED_DATABASE_PASSWORD', '855020180me'),
        environ.get('APPSEED_DATABASE_HOST', '192.168.25.49'),
        environ.get('APPSEED_DATABASE_PORT', 3306),
        environ.get('APPSEED_DATABASE_NAME', 'saba')
    )

    # PostgreSQL database
    # SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
    #     environ.get('APPSEED_DATABASE_USER', 'root'),
    #     environ.get('APPSEED_DATABASE_PASSWORD', '855020180me'),
    #     environ.get('APPSEED_DATABASE_HOST', 'localhost'),
    #     environ.get('APPSEED_DATABASE_PORT', 5432),
    #     environ.get('APPSEED_DATABASE_NAME', 'saba')
    # )

    # For 'in memory' database, please use:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # THEME SUPPORT
    #  if set then url_for('static', filename='', theme='')
    #  will add the theme name to the static URL:
    #    /static/<DEFAULT_THEME>/filename
    # DEFAULT_THEME = "themes/dark"
    DEFAULT_THEME = None

class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        environ.get('APPSEED_DATABASE_USER', 'root'),
        environ.get('APPSEED_DATABASE_PASSWORD', '855020180me'),
        environ.get('APPSEED_DATABASE_HOST', 'avin'),
        environ.get('APPSEED_DATABASE_PORT', 5432),
        environ.get('APPSEED_DATABASE_NAME', 'saba')
    )


class DebugConfig(Config):
    DEBUG = True


config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
