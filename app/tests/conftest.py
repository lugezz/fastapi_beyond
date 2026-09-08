import uuid
from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user, RoleChecker
from app.db.session import get_db
from app.main import app
from app.models.books import Book

mock_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()


def get_mock_session():
    yield mock_session


current_user = get_current_user
role_checker = RoleChecker(['admin'])

app.dependency_overrides[get_db] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[current_user] = Mock()


@pytest.fixture
def fake_session():
    return mock_session


@pytest.fixture
def fake_user_service():
    return mock_user_service


@pytest.fixture
def fake_book_service():
    return mock_book_service


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def test_book():
    return Book(
        uid=uuid.uuid4(),
        user_uid=uuid.uuid4(),
        title="sample title",
        description="sample description",
        page_count=200,
        language="English",
        published_date=datetime.now(),
        update_at=datetime.now()
    )
