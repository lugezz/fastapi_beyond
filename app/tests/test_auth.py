from app.schemas.users import UserCreate

auth_prefix = "/api/v1/auth"


def test_user_creation(test_client, fake_user_service, fake_session):
    signup_data = {
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "password": "securepassword"
    }

    test_client.post(
        url=f"{auth_prefix}/signup",
        json=signup_data
    )

    user_data = UserCreate(**signup_data)

    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(user_data.email)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once_with(user_data, fake_session)
