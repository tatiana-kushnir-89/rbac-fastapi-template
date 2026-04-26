"""
Tests for Role-Based Access Control (RBAC).

Permission Matrix:
| Action              | admin | manager | member |
|---------------------|-------|---------|--------|
| List all users      | ✓     | ✓       | ✗      |
| Create user         | ✓     | ✗       | ✗      |
| View metrics        | ✓     | ✓       | ✗      |
| Update own profile  | ✓     | ✓       | ✓      |
| Update any profile  | ✓     | ✗       | ✗      |
"""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import UserRole
from tests.utils.user import create_user_with_role
from tests.utils.utils import random_email, random_lower_string


class TestListUsers:
    """Test: List all users - admin and manager can access, member cannot."""

    def test_admin_can_list_users(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.ADMIN, client)
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_manager_can_list_users(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MANAGER, client)
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 200
        assert "data" in response.json()

    def test_member_cannot_list_users(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MEMBER, client)
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403


class TestCreateUser:
    """Test: Create user - only admin can create users."""

    def test_admin_can_create_user(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.ADMIN, client)
        data = {
            "email": random_email(),
            "password": random_lower_string(),
        }
        response = client.post(
            f"{settings.API_V1_STR}/users/", headers=headers, json=data
        )
        assert response.status_code == 200
        assert response.json()["email"] == data["email"]

    def test_manager_cannot_create_user(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MANAGER, client)
        data = {
            "email": random_email(),
            "password": random_lower_string(),
        }
        response = client.post(
            f"{settings.API_V1_STR}/users/", headers=headers, json=data
        )
        assert response.status_code == 403

    def test_member_cannot_create_user(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MEMBER, client)
        data = {
            "email": random_email(),
            "password": random_lower_string(),
        }
        response = client.post(
            f"{settings.API_V1_STR}/users/", headers=headers, json=data
        )
        assert response.status_code == 403


class TestViewMetrics:
    """Test: View metrics - admin and manager can access, member cannot."""

    def test_admin_can_view_metrics(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.ADMIN, client)
        response = client.get(f"{settings.API_V1_STR}/metrics/", headers=headers)
        assert response.status_code == 200
        assert "total_users" in response.json()

    def test_manager_can_view_metrics(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MANAGER, client)
        response = client.get(f"{settings.API_V1_STR}/metrics/", headers=headers)
        assert response.status_code == 200
        assert "total_users" in response.json()

    def test_member_cannot_view_metrics(self, client: TestClient, db: Session) -> None:
        _, headers = create_user_with_role(db, UserRole.MEMBER, client)
        response = client.get(f"{settings.API_V1_STR}/metrics/", headers=headers)
        assert response.status_code == 403


class TestUpdateOwnProfile:
    """Test: Update own profile - all roles can update their own profile."""

    def test_admin_can_update_own_profile(
        self, client: TestClient, db: Session
    ) -> None:
        _, headers = create_user_with_role(db, UserRole.ADMIN, client)
        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=headers,
            json={"full_name": "Admin User"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Admin User"

    def test_manager_can_update_own_profile(
        self, client: TestClient, db: Session
    ) -> None:
        _, headers = create_user_with_role(db, UserRole.MANAGER, client)
        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=headers,
            json={"full_name": "Manager User"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Manager User"

    def test_member_can_update_own_profile(
        self, client: TestClient, db: Session
    ) -> None:
        _, headers = create_user_with_role(db, UserRole.MEMBER, client)
        response = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=headers,
            json={"full_name": "Member User"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Member User"


class TestUpdateAnyProfile:
    """Test: Update any profile - only admin can update other users' profiles."""

    def test_admin_can_update_any_profile(
        self, client: TestClient, db: Session
    ) -> None:
        # Create admin
        _, admin_headers = create_user_with_role(db, UserRole.ADMIN, client)
        # Create member to update
        member, _ = create_user_with_role(db, UserRole.MEMBER, client)

        response = client.patch(
            f"{settings.API_V1_STR}/users/{member.id}",
            headers=admin_headers,
            json={"full_name": "Updated by Admin"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated by Admin"

    def test_manager_cannot_update_other_profile(
        self, client: TestClient, db: Session
    ) -> None:
        # Create manager
        _, manager_headers = create_user_with_role(db, UserRole.MANAGER, client)
        # Create member to try to update
        member, _ = create_user_with_role(db, UserRole.MEMBER, client)

        response = client.patch(
            f"{settings.API_V1_STR}/users/{member.id}",
            headers=manager_headers,
            json={"full_name": "Should Fail"},
        )
        assert response.status_code == 403

    def test_member_cannot_update_other_profile(
        self, client: TestClient, db: Session
    ) -> None:
        # Create two members
        member1, member1_headers = create_user_with_role(db, UserRole.MEMBER, client)
        member2, _ = create_user_with_role(db, UserRole.MEMBER, client)

        response = client.patch(
            f"{settings.API_V1_STR}/users/{member2.id}",
            headers=member1_headers,
            json={"full_name": "Should Fail"},
        )
        assert response.status_code == 403