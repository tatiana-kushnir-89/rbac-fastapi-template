# AI-Assisted Development Log: RBAC Implementation

This document captures the development conversation with Claude AI during the implementation of Role-Based Access Control (RBAC) for the FastAPI template.

---

## Session Overview

**Task:** Implement RBAC with three roles (admin, manager, member) for a FastAPI + React template
**Approach:** Iterative development with code review and refactoring
**Result:** Production-ready RBAC with full test coverage

---

## Phase 1: Requirements Analysis

**Developer:**
Let's implement RBAC for this FastAPI template. I need three roles: admin, manager, and member. Before we start coding, what are the architectural options for storing roles, and what are the trade-offs?

**Claude:**
There are three main approaches for role storage:

| Approach | Pros | Cons |
|----------|------|------|
| **Enum field on User** | Simple, single migration, fast queries | Fixed roles, requires migration to add new ones |
| **Separate Role table + FK** | Flexible, can add roles at runtime | More complex, extra JOIN on queries |
| **Many-to-many User-Role** | Multiple roles per user | Most complex, overkill for 3 fixed roles |

**Developer:**
Given that we have a fixed set of three roles and this needs to be implemented efficiently, the enum approach makes sense. What about the authorization pattern on the backend - dependencies vs decorators vs middleware?

**Claude:**
For FastAPI, I recommend dependencies:

```python
# Idiomatic FastAPI approach
AdminUser = Annotated[User, Depends(RoleChecker(UserRole.ADMIN))]

@router.post("/users/")
def create_user(current_user: AdminUser, ...):  # Self-documenting
    ...
```

Benefits:
- Native to FastAPI, type-safe
- Clear in function signatures
- Composable and testable
- Works with OpenAPI documentation

---

## Phase 2: Implementation

**Developer:**
Implement the backend first. Use the enum approach and FastAPI dependencies. Make sure the migration handles existing data safely.

**Claude:**
I'll implement:

1. `UserRole` enum in models.py
2. Role-checking dependencies in deps.py
3. Protected endpoints in users.py
4. New metrics endpoint for admin/manager
5. Migration with `server_default="member"` for existing records

```python
# models.py
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class UserBase(SQLModel):
    role: UserRole = Field(default=UserRole.MEMBER)
```

```python
# deps.py - Initial implementation
def get_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_admin_or_manager(current_user: CurrentUser) -> User:
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(status_code=403, detail="Admin or manager access required")
    return current_user

AdminUser = Annotated[User, Depends(get_admin_user)]
AdminOrManager = Annotated[User, Depends(get_admin_or_manager)]
```

---

## Phase 3: Code Review & Refactoring

**Developer:**
Looking at the deps.py implementation, I see we have separate functions for each role combination. This violates DRY - if we add more roles or combinations, we'll keep adding functions. Can we refactor to a more scalable pattern?

**Claude:**
You're right. Let's refactor to a `RoleChecker` class that's configurable:

```python
class RoleChecker:
    """
    Reusable dependency for role-based authorization.

    Usage:
        @router.get("/", dependencies=[Depends(RoleChecker(UserRole.ADMIN))])

        # Or as typed dependency:
        AdminUser = Annotated[User, Depends(RoleChecker(UserRole.ADMIN))]
    """

    def __init__(self, *allowed_roles: UserRole):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {[r.value for r in self.allowed_roles]}"
            )
        return current_user

# Pre-configured instances
AdminUser = Annotated[User, Depends(RoleChecker(UserRole.ADMIN))]
AdminOrManager = Annotated[User, Depends(RoleChecker(UserRole.ADMIN, UserRole.MANAGER))]
```

This pattern:
- Single class handles any role combination
- Easy to add new combinations
- Clear error messages with required roles
- Documented with usage examples

**Developer:**
Now let's apply the same principle to the frontend. I see permission checks scattered across components. How should we centralize this?

**Claude:**
Create a centralized permissions module:

```typescript
// utils/rbac.ts
export type UserRole = "admin" | "manager" | "member"

export function hasRole(
  userRole: string | undefined,
  allowedRoles: UserRole | UserRole[]
): boolean {
  if (!userRole) return false
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles]
  return roles.includes(userRole as UserRole)
}

export const permissions = {
  canListUsers: (role?: string) => hasRole(role, ["admin", "manager"]),
  canCreateUsers: (role?: string) => hasRole(role, "admin"),
  canUpdateAnyUser: (role?: string) => hasRole(role, "admin"),
  canDeleteUsers: (role?: string) => hasRole(role, "admin"),
  canViewMetrics: (role?: string) => hasRole(role, ["admin", "manager"]),
}
```

Then use in components:

```typescript
// Route guard
beforeLoad: async () => {
  const user = await UsersService.readUserMe()
  if (!permissions.canViewMetrics(user.role)) {
    throw redirect({ to: "/" })
  }
}

// Conditional rendering
{permissions.canCreateUsers(user?.role) && <AddUser />}
```

Benefits:
- Single source of truth for permissions
- Easy to update when requirements change
- Type-safe with UserRole type
- Testable in isolation

---

## Phase 4: Final Review

**Developer:**
Let's do a final review. Are there any remaining issues or potential improvements we should note?

**Claude:**
**Current state - Production ready:**

| Component | Status |
|-----------|--------|
| RoleChecker class | Clean, extensible pattern |
| Typed dependencies | Idiomatic FastAPI |
| Frontend permissions | Centralized in rbac.ts |
| Route guards | beforeLoad + redirect |
| Tests | 15 tests covering full permission matrix |
| Migration | Safe with server_default |

**Non-critical improvements for future:**

1. **Metrics endpoint optimization** - Currently N+3 queries (N = roles). Could use GROUP BY:
```python
# Future optimization
session.exec(
    select(User.role, func.count())
    .group_by(User.role)
)
```

2. **is_superuser coexistence** - Both `is_superuser` and `role` exist. Kept for backward compatibility with original template.

3. **Permission-based system** - Current role-based system could evolve to permission-based (roles contain permissions) if requirements grow.

---

## Permission Matrix

| Action | admin | manager | member |
|--------|:-----:|:-------:|:------:|
| List all users | ✓ | ✓ | ✗ |
| Create user | ✓ | ✗ | ✗ |
| View metrics | ✓ | ✓ | ✗ |
| Update own profile | ✓ | ✓ | ✓ |
| Update any profile | ✓ | ✗ | ✗ |
| Delete user | ✓ | ✗ | ✗ |

---

## Files Modified

### Backend

| File | Changes |
|------|---------|
| `app/models.py` | `UserRole` enum, `role` field, `Metrics` model |
| `app/api/deps.py` | `RoleChecker` class, `AdminUser`, `AdminOrManager` |
| `app/api/routes/users.py` | Role-based endpoint protection |
| `app/api/routes/metrics.py` | New metrics endpoint |
| `app/api/main.py` | Registered metrics router |
| `app/core/db.py` | First superuser gets ADMIN role |
| `alembic/versions/add_role_to_user.py` | Migration with server_default |
| `tests/api/routes/test_rbac.py` | 15 RBAC tests |
| `tests/utils/user.py` | `create_user_with_role()` helper |

### Frontend

| File | Changes |
|------|---------|
| `src/utils/rbac.ts` | Centralized permissions |
| `src/hooks/useAuth.ts` | Role helpers integration |
| `src/components/Sidebar/AppSidebar.tsx` | Conditional navigation |
| `src/routes/_layout/admin.tsx` | Route guard, conditional AddUser |
| `src/routes/_layout/metrics.tsx` | New metrics page |
| `src/client/services/MetricsService.ts` | Metrics API service |

---

## Test Coverage

```
tests/api/routes/test_rbac.py
├── TestListUsers (3 tests)
│   ├── test_admin_can_list_users
│   ├── test_manager_can_list_users
│   └── test_member_cannot_list_users
├── TestCreateUser (3 tests)
│   ├── test_admin_can_create_user
│   ├── test_manager_cannot_create_user
│   └── test_member_cannot_create_user
├── TestViewMetrics (3 tests)
│   ├── test_admin_can_view_metrics
│   ├── test_manager_can_view_metrics
│   └── test_member_cannot_view_metrics
├── TestUpdateOwnProfile (3 tests)
│   └── all roles can update own profile
└── TestUpdateAnyProfile (3 tests)
    ├── test_admin_can_update_any_profile
    ├── test_manager_cannot_update_other_profile
    └── test_member_cannot_update_other_profile
```

---

*Development assisted by Claude AI (Opus 4.5)*