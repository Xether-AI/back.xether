"""Permissions and Role management."""

from enum import Enum
from typing import List
from fastapi import Depends, HTTPException, status

from app.api import deps
from app.models.base import User


class Role(str, Enum):
    """System roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions."""
    # User Management
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    
    # Team Management
    TEAMS_READ = "teams:read"
    TEAMS_WRITE = "teams:write"
    
    # Project Management
    PROJECTS_READ = "projects:read"
    PROJECTS_WRITE = "projects:write"
    
    # Dataset Management
    DATASETS_READ = "datasets:read"
    DATASETS_WRITE = "datasets:write"
    
    # Pipeline Management
    PIPELINES_READ = "pipelines:read"
    PIPELINES_WRITE = "pipelines:write"
    PIPELINES_EXECUTE = "pipelines:execute"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],
    Role.MANAGER: [
        Permission.USERS_READ,
        Permission.TEAMS_READ,
        Permission.PROJECTS_READ,
        Permission.PROJECTS_WRITE,
        Permission.DATASETS_READ,
        Permission.DATASETS_WRITE,
        Permission.PIPELINES_READ,
        Permission.PIPELINES_WRITE,
        Permission.PIPELINES_EXECUTE,
    ],
    Role.DEVELOPER: [
        Permission.PROJECTS_READ,
        Permission.DATASETS_READ,
        Permission.DATASETS_WRITE,
        Permission.PIPELINES_READ,
        Permission.PIPELINES_WRITE,
        Permission.PIPELINES_EXECUTE,
    ],
    Role.VIEWER: [
        Permission.PROJECTS_READ,
        Permission.DATASETS_READ,
        Permission.PIPELINES_READ,
    ],
}


class PermissionChecker:
    """Dependency for checking resource permissions."""

    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions

    def __call__(self, user: User = Depends(deps.get_current_active_user)):
        # Superuser bypass
        if user.is_superuser:
            return True
            
        # Check roles and permissions
        user_permissions = []
        if hasattr(user, "role") and user.role:
            user_permissions.extend(ROLE_PERMISSIONS.get(user.role, []))
            
        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {perm.value}",
                )
        return True
