"""
Database service for the Authentication Service.

This module handles all database operations including connection management,
session handling, and database utilities.
"""

import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging

from ..models.database import Base, User, Session, Role, UserRole, AuditLog, PasswordResetToken, MFABackupCode

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for handling all database operations."""
    
    def __init__(self, database_url: str):
        """Initialize the database service."""
        self.database_url = database_url
        self.engine = None
        self.async_session_maker = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the database connection and create tables."""
        if self._initialized:
            return
        
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                pool_size=10,
                max_overflow=20
            )
            
            # Create async session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Test connection
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            
            self._initialized = True
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise
    
    async def close(self):
        """Close the database connection."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database service closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get a database session."""
        if not self._initialized:
            await self.initialize()
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        async with self.get_session() as session:
            user = User(**user_data)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            return result.fetchone()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": email}
            )
            return result.fetchone()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE username = :username"),
                {"username": username}
            )
            return result.fetchone()
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    UPDATE users 
                    SET updated_at = NOW(), 
                        first_name = COALESCE(:first_name, first_name),
                        last_name = COALESCE(:last_name, last_name),
                        username = COALESCE(:username, username),
                        status = COALESCE(:status, status),
                        email_verified = COALESCE(:email_verified, email_verified),
                        mfa_enabled = COALESCE(:mfa_enabled, mfa_enabled),
                        mfa_secret = COALESCE(:mfa_secret, mfa_secret),
                        last_login = COALESCE(:last_login, last_login),
                        metadata = COALESCE(:metadata, metadata)
                    WHERE id = :user_id
                    RETURNING *
                """),
                {**update_data, "user_id": user_id}
            )
            return result.fetchone()
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        async with self.get_session() as session:
            result = await session.execute(
                text("DELETE FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )
            return result.rowcount > 0
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :skip"),
                {"limit": limit, "skip": skip}
            )
            return result.fetchall()
    
    async def count_users(self) -> int:
        """Count total users."""
        async with self.get_session() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            return result.scalar()
    
    # Session operations
    async def create_session(self, session_data: Dict[str, Any]) -> Session:
        """Create a new session."""
        async with self.get_session() as session:
            db_session = Session(**session_data)
            session.add(db_session)
            await session.flush()
            await session.refresh(db_session)
            return db_session
    
    async def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM sessions WHERE id = :session_id"),
                {"session_id": session_id}
            )
            return result.fetchone()
    
    async def get_session_by_token_hash(self, token_hash: str) -> Optional[Session]:
        """Get session by token hash."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM sessions WHERE token_hash = :token_hash AND is_active = true"),
                {"token_hash": token_hash}
            )
            return result.fetchone()
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> Optional[Session]:
        """Update session information."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    UPDATE sessions 
                    SET last_used_at = COALESCE(:last_used_at, last_used_at),
                        is_active = COALESCE(:is_active, is_active)
                    WHERE id = :session_id
                    RETURNING *
                """),
                {**update_data, "session_id": session_id}
            )
            return result.fetchone()
    
    async def revoke_session(self, session_id: str) -> bool:
        """Revoke a session."""
        async with self.get_session() as session:
            result = await session.execute(
                text("UPDATE sessions SET is_active = false WHERE id = :session_id"),
                {"session_id": session_id}
            )
            return result.rowcount > 0
    
    async def revoke_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user."""
        async with self.get_session() as session:
            result = await session.execute(
                text("UPDATE sessions SET is_active = false WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            return result.rowcount
    
    async def list_user_sessions(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Session]:
        """List user sessions with pagination."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT * FROM sessions 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC 
                    LIMIT :limit OFFSET :skip
                """),
                {"user_id": user_id, "limit": limit, "skip": skip}
            )
            return result.fetchall()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        async with self.get_session() as session:
            result = await session.execute(
                text("DELETE FROM sessions WHERE expires_at < NOW()")
            )
            return result.rowcount
    
    # Role operations
    async def create_role(self, role_data: Dict[str, Any]) -> Role:
        """Create a new role."""
        async with self.get_session() as session:
            role = Role(**role_data)
            session.add(role)
            await session.flush()
            await session.refresh(role)
            return role
    
    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM roles WHERE id = :role_id"),
                {"role_id": role_id}
            )
            return result.fetchone()
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM roles WHERE name = :name"),
                {"name": name}
            )
            return result.fetchone()
    
    async def update_role(self, role_id: str, update_data: Dict[str, Any]) -> Optional[Role]:
        """Update role information."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    UPDATE roles 
                    SET updated_at = NOW(),
                        name = COALESCE(:name, name),
                        description = COALESCE(:description, description),
                        permissions = COALESCE(:permissions, permissions)
                    WHERE id = :role_id
                    RETURNING *
                """),
                {**update_data, "role_id": role_id}
            )
            return result.fetchone()
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        async with self.get_session() as session:
            result = await session.execute(
                text("DELETE FROM roles WHERE id = :role_id"),
                {"role_id": role_id}
            )
            return result.rowcount > 0
    
    async def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """List roles with pagination."""
        async with self.get_session() as session:
            result = await session.execute(
                text("SELECT * FROM roles ORDER BY created_at DESC LIMIT :limit OFFSET :skip"),
                {"limit": limit, "skip": skip}
            )
            return result.fetchall()
    
    # User-Role operations
    async def assign_role_to_user(self, user_id: str, role_id: str, assigned_by: str = None) -> bool:
        """Assign a role to a user."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    INSERT INTO user_roles (user_id, role_id, assigned_by)
                    VALUES (:user_id, :role_id, :assigned_by)
                    ON CONFLICT (user_id, role_id) DO NOTHING
                """),
                {"user_id": user_id, "role_id": role_id, "assigned_by": assigned_by}
            )
            return result.rowcount > 0
    
    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Remove a role from a user."""
        async with self.get_session() as session:
            result = await session.execute(
                text("DELETE FROM user_roles WHERE user_id = :user_id AND role_id = :role_id"),
                {"user_id": user_id, "role_id": role_id}
            )
            return result.rowcount > 0
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT r.* FROM roles r
                    JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = :user_id
                """),
                {"user_id": user_id}
            )
            return result.fetchall()
    
    # Audit log operations
    async def create_audit_log(self, audit_data: Dict[str, Any]) -> AuditLog:
        """Create a new audit log entry."""
        async with self.get_session() as session:
            audit_log = AuditLog(**audit_data)
            session.add(audit_log)
            await session.flush()
            await session.refresh(audit_log)
            return audit_log
    
    async def list_audit_logs(self, user_id: str = None, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """List audit logs with pagination."""
        async with self.get_session() as session:
            if user_id:
                result = await session.execute(
                    text("""
                        SELECT * FROM audit_logs 
                        WHERE user_id = :user_id 
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :skip
                    """),
                    {"user_id": user_id, "limit": limit, "skip": skip}
                )
            else:
                result = await session.execute(
                    text("""
                        SELECT * FROM audit_logs 
                        ORDER BY created_at DESC 
                        LIMIT :limit OFFSET :skip
                    """),
                    {"limit": limit, "skip": skip}
                )
            return result.fetchall()
    
    # Password reset operations
    async def create_password_reset_token(self, token_data: Dict[str, Any]) -> PasswordResetToken:
        """Create a new password reset token."""
        async with self.get_session() as session:
            token = PasswordResetToken(**token_data)
            session.add(token)
            await session.flush()
            await session.refresh(token)
            return token
    
    async def get_password_reset_token(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Get password reset token by hash."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT * FROM password_reset_tokens 
                    WHERE token_hash = :token_hash AND expires_at > NOW() AND used_at IS NULL
                """),
                {"token_hash": token_hash}
            )
            return result.fetchone()
    
    async def mark_password_reset_token_used(self, token_id: str) -> bool:
        """Mark a password reset token as used."""
        async with self.get_session() as session:
            result = await session.execute(
                text("UPDATE password_reset_tokens SET used_at = NOW() WHERE id = :token_id"),
                {"token_id": token_id}
            )
            return result.rowcount > 0
    
    async def cleanup_expired_password_reset_tokens(self) -> int:
        """Clean up expired password reset tokens."""
        async with self.get_session() as session:
            result = await session.execute(
                text("DELETE FROM password_reset_tokens WHERE expires_at < NOW()")
            )
            return result.rowcount
    
    # MFA operations
    async def create_mfa_backup_code(self, code_data: Dict[str, Any]) -> MFABackupCode:
        """Create a new MFA backup code."""
        async with self.get_session() as session:
            backup_code = MFABackupCode(**code_data)
            session.add(backup_code)
            await session.flush()
            await session.refresh(backup_code)
            return backup_code
    
    async def get_mfa_backup_code(self, code_hash: str) -> Optional[MFABackupCode]:
        """Get MFA backup code by hash."""
        async with self.get_session() as session:
            result = await session.execute(
                text("""
                    SELECT * FROM mfa_backup_codes 
                    WHERE code_hash = :code_hash AND used_at IS NULL
                """),
                {"code_hash": code_hash}
            )
            return result.fetchone()
    
    async def mark_mfa_backup_code_used(self, code_id: str) -> bool:
        """Mark an MFA backup code as used."""
        async with self.get_session() as session:
            result = await session.execute(
                text("UPDATE mfa_backup_codes SET used_at = NOW() WHERE id = :code_id"),
                {"code_id": code_id}
            )
            return result.rowcount > 0 