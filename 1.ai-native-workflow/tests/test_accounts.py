import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_signup_creates_user_and_logs_in(client):
    response = client.post(
        "/signup/",
        {
            "username": "priya",
            "display_name": "Priya Raman",
            "password1": "a-very-unlikely-password-42",
            "password2": "a-very-unlikely-password-42",
        },
    )

    assert response.status_code == 302
    assert response.url == "/"
    user = User.objects.get(username="priya")
    assert user.display_name == "Priya Raman"
    assert "_auth_user_id" in client.session


def test_signup_with_duplicate_username_shows_form_error(client):
    User.objects.create_user(username="priya", password="whatever-1234")

    response = client.post(
        "/signup/",
        {
            "username": "priya",
            "display_name": "Someone Else",
            "password1": "a-very-unlikely-password-42",
            "password2": "a-very-unlikely-password-42",
        },
    )

    assert response.status_code == 200
    assert "already exists" in response.content.decode().lower()
    assert User.objects.filter(username="priya").count() == 1


def test_signup_with_weak_password_is_rejected(client):
    response = client.post(
        "/signup/",
        {
            "username": "sam",
            "display_name": "Sam Okafor",
            "password1": "12345678",
            "password2": "12345678",
        },
    )

    assert response.status_code == 200
    assert not User.objects.filter(username="sam").exists()


def test_login_with_correct_credentials_succeeds(client):
    User.objects.create_user(username="priya", password="correct-horse-battery")

    response = client.post(
        "/accounts/login/", {"username": "priya", "password": "correct-horse-battery"}
    )

    assert response.status_code == 302
    assert "_auth_user_id" in client.session


def test_login_with_wrong_password_fails(client):
    User.objects.create_user(username="priya", password="correct-horse-battery")

    response = client.post("/accounts/login/", {"username": "priya", "password": "wrong"})

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_logout_clears_session(client):
    User.objects.create_user(username="priya", password="correct-horse-battery")
    client.login(username="priya", password="correct-horse-battery")

    response = client.post("/accounts/logout/")

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session
