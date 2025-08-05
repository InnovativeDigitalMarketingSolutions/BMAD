"""
User Management Module

Provides user management, role-based access control (RBAC), and permission management
for enterprise BMAD deployments.
"""

import uuid
import json
import logging
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, UTC
from enum import Enum

logger = logging.getLogger(__name__)


class UserStatus(Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Permission(Enum):
    """Permission enumeration."""
    # Agent permissions
    VIEW_AGENTS = "view_agents"
    CREATE_AGENTS = "create_agents"
    EDIT_AGENTS = "edit_agents"
    DELETE_AGENTS = "delete_agents"
    EXECUTE_AGENTS = "execute_agents"
    
    # Workflow permissions
    VIEW_WORKFLOWS = "view_workflows"
    CREATE_WORKFLOWS = "create_workflows"
    EDIT_WORKFLOWS = "edit_workflows"
    DELETE_WORKFLOWS = "delete_workflows"
    EXECUTE_WORKFLOWS = "execute_workflows"
    
    # User management permissions
    VIEW_USERS = "view_users"
    CREATE_USERS = "create_users"
    EDIT_USERS = "edit_users"
    DELETE_USERS = "delete_users"
    
    # System permissions
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    MANAGE_BILLING = "manage_billing"


@dataclass
class Role:
    """Represents a role in the RBAC system."""
    id: str
    name: str
    description: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime
    is_system: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert role to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """Create role from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class User:
    """Represents a user in the system."""
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    tenant_id: str
    role_ids: List[str]
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['status'] = self.status.value
        if self.last_login:
            data['last_login'] = self.last_login.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        data['status'] = UserStatus(data['status'])
        if data.get('last_login'):
            data['last_login'] = datetime.fromisoformat(data['last_login'])
        return cls(**data)


class UserManager:
    """Manages user operations."""
    
    def __init__(self, storage_path: str = "data/users"):
        self.storage_path = storage_path
        self.users: Dict[str, User] = {}
        self._load_users()
    
    def _load_users(self):
        """Load users from storage."""
        try:
            import os
            from pathlib import Path
            
            user_file = Path(self.storage_path) / "users.json"
            if user_file.exists():
                with open(user_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data.values():
                        user = User.from_dict(user_data)
                        self.users[user.id] = user
                logger.info(f"Loaded {len(self.users)} users from storage")
        except Exception as e:
            logger.warning(f"Could not load users: {e}")
    
    def _save_users(self):
        """Save users to storage."""
        try:
            import os
            from pathlib import Path
            
            user_file = Path(self.storage_path) / "users.json"
            user_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {uid: user.to_dict() for uid, user in self.users.items()}
            with open(user_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using secure method."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_hex = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def create_user(self, email: str, username: str, first_name: str, last_name: str,
                   tenant_id: str, password: str, role_ids: List[str] = None) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        if role_ids is None:
            role_ids = []
        
        user = User(
            id=user_id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            tenant_id=tenant_id,
            role_ids=role_ids,
            status=UserStatus.PENDING,
            created_at=now,
            updated_at=now,
            password_hash=self._hash_password(password)
        )
        
        self.users[user_id] = user
        self._save_users()
        logger.info(f"Created user: {email} ({user_id})")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user or not user.password_hash:
            return None
        
        if not self._verify_password(password, user.password_hash):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Update last login
        user.last_login = datetime.now(UTC)
        self._save_users()
        
        return user
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user properties."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.now(UTC)
        self._save_users()
        logger.info(f"Updated user: {user.email}")
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.users.get(user_id)
        if not user:
            return False
        
        del self.users[user_id]
        self._save_users()
        logger.info(f"Deleted user: {user.email}")
        return True
    
    def list_users_by_tenant(self, tenant_id: str) -> List[User]:
        """List users by tenant."""
        return [user for user in self.users.values() if user.tenant_id == tenant_id]


class RoleManager:
    """Manages role operations."""
    
    def __init__(self, storage_path: str = "data/roles"):
        self.storage_path = storage_path
        self.roles: Dict[str, Role] = {}
        self._load_roles()
        self._create_default_roles()
    
    def _load_roles(self):
        """Load roles from storage."""
        try:
            import os
            from pathlib import Path
            
            role_file = Path(self.storage_path) / "roles.json"
            if role_file.exists():
                with open(role_file, 'r') as f:
                    data = json.load(f)
                    for role_data in data.values():
                        role = Role.from_dict(role_data)
                        self.roles[role.id] = role
                logger.info(f"Loaded {len(self.roles)} roles from storage")
        except Exception as e:
            logger.warning(f"Could not load roles: {e}")
    
    def _save_roles(self):
        """Save roles to storage."""
        try:
            import os
            from pathlib import Path
            
            role_file = Path(self.storage_path) / "roles.json"
            role_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {rid: role.to_dict() for rid, role in self.roles.items()}
            with open(role_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save roles: {e}")
    
    def _create_default_roles(self):
        """Create default system roles if they don't exist."""
        if not self.roles:
            now = datetime.now(UTC)
            
            # Admin role
            admin_role = Role(
                id=str(uuid.uuid4()),
                name="admin",
                description="Full system administrator",
                permissions=[p.value for p in Permission],
                created_at=now,
                updated_at=now,
                is_system=True
            )
            
            # User role
            user_role = Role(
                id=str(uuid.uuid4()),
                name="user",
                description="Standard user",
                permissions=[
                    Permission.VIEW_AGENTS.value,
                    Permission.EXECUTE_AGENTS.value,
                    Permission.VIEW_WORKFLOWS.value,
                    Permission.EXECUTE_WORKFLOWS.value
                ],
                created_at=now,
                updated_at=now,
                is_system=True
            )
            
            # Viewer role
            viewer_role = Role(
                id=str(uuid.uuid4()),
                name="viewer",
                description="Read-only user",
                permissions=[
                    Permission.VIEW_AGENTS.value,
                    Permission.VIEW_WORKFLOWS.value
                ],
                created_at=now,
                updated_at=now,
                is_system=True
            )
            
            self.roles[admin_role.id] = admin_role
            self.roles[user_role.id] = user_role
            self.roles[viewer_role.id] = viewer_role
            self._save_roles()
    
    def create_role(self, name: str, description: str, permissions: List[str]) -> Role:
        """Create a new role."""
        role_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        
        role = Role(
            id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            created_at=now,
            updated_at=now
        )
        
        self.roles[role_id] = role
        self._save_roles()
        logger.info(f"Created role: {name} ({role_id})")
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.roles.get(role_id)
    
    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        for role in self.roles.values():
            if role.name == name:
                return role
        return None
    
    def update_role(self, role_id: str, **kwargs) -> Optional[Role]:
        """Update role properties."""
        role = self.roles.get(role_id)
        if not role:
            return None
        
        for key, value in kwargs.items():
            if hasattr(role, key):
                setattr(role, key, value)
        
        role.updated_at = datetime.now(UTC)
        self._save_roles()
        logger.info(f"Updated role: {role.name}")
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        role = self.roles.get(role_id)
        if not role:
            return False
        
        if role.is_system:
            logger.warning(f"Cannot delete system role: {role.name}")
            return False
        
        del self.roles[role_id]
        self._save_roles()
        logger.info(f"Deleted role: {role.name}")
        return True
    
    def list_roles(self) -> List[Role]:
        """List all roles."""
        return list(self.roles.values())
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        user = self.user_manager.get_user(user_id)
        if not user:
            return []
        
        roles = []
        for role_id in user.role_ids:
            role = self.get_role(role_id)
            if role:
                roles.append(role)
        
        return roles


class PermissionManager:
    """Manages permission checking."""
    
    def __init__(self, user_manager: UserManager, role_manager: RoleManager):
        self.user_manager = user_manager
        self.role_manager = role_manager
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user."""
        user = self.user_manager.get_user(user_id)
        if not user:
            return set()
        
        permissions = set()
        for role_id in user.role_ids:
            role = self.role_manager.get_role(role_id)
            if role:
                permissions.update(role.permissions)
        
        return permissions
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def has_any_permission(self, user_id: str, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        user_permissions = self.get_user_permissions(user_id)
        return any(perm in user_permissions for perm in permissions)
    
    def has_all_permissions(self, user_id: str, permissions: List[str]) -> bool:
        """Check if user has all of the specified permissions."""
        user_permissions = self.get_user_permissions(user_id)
        return all(perm in user_permissions for perm in permissions)
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        return self.role_manager.get_user_roles(user_id)
    
    def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role."""
        user_roles = self.get_user_roles(user_id)
        return any(role.name == role_name for role in user_roles)
    
    def has_any_role(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        user_roles = self.get_user_roles(user_id)
        return any(role.name in role_names for role in user_roles)
    
    def has_all_roles(self, user_id: str, role_names: List[str]) -> bool:
        """Check if user has all of the specified roles."""
        user_roles = self.get_user_roles(user_id)
        user_role_names = [role.name for role in user_roles]
        return all(role_name in user_role_names for role_name in role_names)
    
    def get_user_permissions_by_tenant(self, user_id: str, tenant_id: str) -> Set[str]:
        """Get user permissions filtered by tenant."""
        user = self.user_manager.get_user(user_id)
        if not user or user.tenant_id != tenant_id:
            return set()
        
        return self.get_user_permissions(user_id)
    
    def check_tenant_permission(self, user_id: str, tenant_id: str, permission: str) -> bool:
        """Check if user has permission in specific tenant."""
        return permission in self.get_user_permissions_by_tenant(user_id, tenant_id)


# Global instances
user_manager = UserManager()
role_manager = RoleManager()
permission_manager = PermissionManager(user_manager, role_manager) 