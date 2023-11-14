import os

import pytest
from flask import template_rendered

from styloexport import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {"TESTING": True, "WTF_CSRF_ENABLED": False, "SE_DOWNLOAD_DIR": tmp_path}
    )
    os.environ[
        "SE_ALLOWED_INSTANCE_BASE_URLS"
    ] = "https://stylo.huma-num.fr http://localhost:3000"
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def context(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append(context)

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
