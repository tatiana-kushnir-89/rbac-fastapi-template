from typing import Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import AdminOrManager, SessionDep
from app.models import Item, Metrics, User, UserRole

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", response_model=Metrics)
def get_metrics(session: SessionDep, current_user: AdminOrManager) -> Any:
    """
    Get system metrics. Requires admin or manager role.
    """
    # Total users
    total_users = session.exec(select(func.count()).select_from(User)).one()

    # Active users
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active == True)
    ).one()

    # Total items
    total_items = session.exec(select(func.count()).select_from(Item)).one()

    # Users by role
    users_by_role = {}
    for role in UserRole:
        count = session.exec(
            select(func.count()).select_from(User).where(User.role == role)
        ).one()
        users_by_role[role.value] = count

    return Metrics(
        total_users=total_users,
        active_users=active_users,
        total_items=total_items,
        users_by_role=users_by_role,
    )