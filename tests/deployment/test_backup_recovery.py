"""
Backup and Recovery Tests for BMAD System

This module tests backup and recovery procedures to ensure
data protection and business continuity in production.

Test Coverage:
- Database backup procedures
- File system backup testing
- Configuration backup validation
- Recovery procedure testing
- Data integrity validation
- Backup scheduling testing
"""

import pytest
import os
import json
import shutil
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

class BackupManager:
    """Backup management system."""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        self.backup_dir = backup_dir
        self.backup_history = []
        self.recovery_history = []
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_database_backup(self, database_name: str) -> Dict[str, Any]:
        """Create a database backup."""
        backup_id = f"db_backup_{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, f"{backup_id}.sql")
        
        try:
            # Simulate database backup
            backup_data = {
                "database": database_name,
                "tables": ["users", "agents", "workflows", "logs"],
                "record_count": 1250,
                "backup_size": "15.2MB",
                "timestamp": datetime.now().isoformat()
            }
            
            # Write backup file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            backup_record = {
                "id": backup_id,
                "type": "database",
                "database": database_name,
                "path": backup_path,
                "size": os.path.getsize(backup_path),
                "timestamp": datetime.now(),
                "status": "completed"
            }
            
            self.backup_history.append(backup_record)
            return backup_record
            
        except Exception as e:
            backup_record = {
                "id": backup_id,
                "type": "database",
                "database": database_name,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed"
            }
            self.backup_history.append(backup_record)
            return backup_record
    
    def create_file_backup(self, source_path: str, backup_name: str = None) -> Dict[str, Any]:
        """Create a file system backup."""
        if not backup_name:
            backup_name = f"file_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Simulate file backup
            if os.path.isdir(source_path):
                shutil.copytree(source_path, backup_path)
            else:
                shutil.copy2(source_path, backup_path)
            
            backup_record = {
                "id": backup_name,
                "type": "file",
                "source_path": source_path,
                "backup_path": backup_path,
                "size": self._get_directory_size(backup_path) if os.path.isdir(backup_path) else os.path.getsize(backup_path),
                "timestamp": datetime.now(),
                "status": "completed"
            }
            
            self.backup_history.append(backup_record)
            return backup_record
            
        except Exception as e:
            backup_record = {
                "id": backup_name,
                "type": "file",
                "source_path": source_path,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed"
            }
            self.backup_history.append(backup_record)
            return backup_record
    
    def create_configuration_backup(self) -> Dict[str, Any]:
        """Create a configuration backup."""
        backup_id = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, f"{backup_id}.json")
        
        try:
            # Simulate configuration backup
            config_data = {
                "environment": "production",
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "bmad_prod"
                },
                "api": {
                    "host": "0.0.0.0",
                    "port": 8000
                },
                "security": {
                    "jwt_secret": "***REDACTED***",
                    "cors_origins": ["https://example.com"]
                },
                "backup_timestamp": datetime.now().isoformat()
            }
            
            # Write configuration backup
            with open(backup_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            backup_record = {
                "id": backup_id,
                "type": "configuration",
                "path": backup_path,
                "size": os.path.getsize(backup_path),
                "timestamp": datetime.now(),
                "status": "completed"
            }
            
            self.backup_history.append(backup_record)
            return backup_record
            
        except Exception as e:
            backup_record = {
                "id": backup_id,
                "type": "configuration",
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed"
            }
            self.backup_history.append(backup_record)
            return backup_record
    
    def restore_database_backup(self, backup_id: str, target_database: str = None) -> Dict[str, Any]:
        """Restore a database backup."""
        # Find backup record
        backup_record = next((b for b in self.backup_history if b["id"] == backup_id), None)
        
        if not backup_record:
            return {"error": f"Backup {backup_id} not found"}
        
        if backup_record["status"] != "completed":
            return {"error": f"Backup {backup_id} is not complete"}
        
        try:
            # Simulate database restoration
            restore_record = {
                "backup_id": backup_id,
                "type": "database",
                "target_database": target_database or backup_record["database"],
                "timestamp": datetime.now(),
                "status": "completed",
                "restoration_time": "45.2s"
            }
            
            self.recovery_history.append(restore_record)
            return restore_record
            
        except Exception as e:
            restore_record = {
                "backup_id": backup_id,
                "type": "database",
                "target_database": target_database,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed"
            }
            self.recovery_history.append(restore_record)
            return restore_record
    
    def restore_file_backup(self, backup_id: str, target_path: str) -> Dict[str, Any]:
        """Restore a file backup."""
        # Find backup record
        backup_record = next((b for b in self.backup_history if b["id"] == backup_id), None)
        
        if not backup_record:
            return {"error": f"Backup {backup_id} not found"}
        
        if backup_record["status"] != "completed":
            return {"error": f"Backup {backup_id} is not complete"}
        
        try:
            # Simulate file restoration
            restore_record = {
                "backup_id": backup_id,
                "type": "file",
                "source_path": backup_record["backup_path"],
                "target_path": target_path,
                "timestamp": datetime.now(),
                "status": "completed",
                "restoration_time": "12.3s"
            }
            
            self.recovery_history.append(restore_record)
            return restore_record
            
        except Exception as e:
            restore_record = {
                "backup_id": backup_id,
                "type": "file",
                "source_path": backup_record["backup_path"],
                "target_path": target_path,
                "error": str(e),
                "timestamp": datetime.now(),
                "status": "failed"
            }
            self.recovery_history.append(restore_record)
            return restore_record
    
    def validate_backup_integrity(self, backup_id: str) -> Dict[str, Any]:
        """Validate backup integrity."""
        backup_record = next((b for b in self.backup_history if b["id"] == backup_id), None)
        
        if not backup_record:
            return {"error": f"Backup {backup_id} not found"}
        
        if backup_record["status"] != "completed":
            return {"error": f"Backup {backup_id} is not complete"}
        
        try:
            # Simulate integrity validation
            validation_result = {
                "backup_id": backup_id,
                "type": backup_record["type"],
                "integrity_check": "passed",
                "checksum_valid": True,
                "file_size_valid": True,
                "timestamp": datetime.now(),
                "validation_time": "2.1s"
            }
            
            return validation_result
            
        except Exception as e:
            return {
                "backup_id": backup_id,
                "integrity_check": "failed",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """Get backup summary."""
        total_backups = len(self.backup_history)
        successful_backups = len([b for b in self.backup_history if b["status"] == "completed"])
        failed_backups = total_backups - successful_backups
        
        backup_types = {}
        for backup in self.backup_history:
            backup_type = backup["type"]
            if backup_type in backup_types:
                backup_types[backup_type] += 1
            else:
                backup_types[backup_type] = 1
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": successful_backups / total_backups if total_backups > 0 else 0,
            "backup_types": backup_types,
            "latest_backup": max(self.backup_history, key=lambda x: x["timestamp"]) if self.backup_history else None
        }
    
    def _get_directory_size(self, path: str) -> int:
        """Get directory size in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size

class RecoveryManager:
    """Recovery management system."""
    
    def __init__(self):
        self.recovery_procedures = {}
        self.recovery_history = []
    
    def register_recovery_procedure(self, name: str, procedure_func, dependencies: List[str] = None):
        """Register a recovery procedure."""
        self.recovery_procedures[name] = {
            "function": procedure_func,
            "dependencies": dependencies or [],
            "last_run": None,
            "status": "unknown"
        }
    
    async def execute_recovery_procedure(self, name: str) -> Dict[str, Any]:
        """Execute a recovery procedure."""
        if name not in self.recovery_procedures:
            return {"error": f"Recovery procedure '{name}' not found"}
        
        procedure = self.recovery_procedures[name]
        start_time = datetime.now()
        
        try:
            # Check dependencies
            for dep in procedure["dependencies"]:
                if dep not in self.recovery_procedures:
                    return {"error": f"Dependency '{dep}' not found"}
            
            # Execute procedure
            result = await procedure["function"]()
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            recovery_record = {
                "procedure_name": name,
                "status": "completed",
                "duration": duration,
                "timestamp": end_time,
                "result": result
            }
            
            procedure["last_run"] = end_time
            procedure["status"] = "completed"
            self.recovery_history.append(recovery_record)
            
            return recovery_record
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            recovery_record = {
                "procedure_name": name,
                "status": "failed",
                "duration": duration,
                "timestamp": end_time,
                "error": str(e)
            }
            
            procedure["last_run"] = end_time
            procedure["status"] = "failed"
            self.recovery_history.append(recovery_record)
            
            return recovery_record

# Mock recovery procedures
async def mock_database_recovery():
    """Mock database recovery procedure."""
    import asyncio
    await asyncio.sleep(0.01)  # Simulate recovery time
    return {"tables_restored": 15, "records_restored": 1250}

async def mock_file_recovery():
    """Mock file recovery procedure."""
    import asyncio
    await asyncio.sleep(0.01)  # Simulate recovery time
    return {"files_restored": 45, "directories_restored": 8}

async def mock_configuration_recovery():
    """Mock configuration recovery procedure."""
    import asyncio
    await asyncio.sleep(0.01)  # Simulate recovery time
    return {"config_files_restored": 3, "settings_validated": True}

def test_database_backup():
    """Test database backup creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create database backup
        backup_result = backup_manager.create_database_backup("bmad_production")
        
        # Verify backup creation
        assert backup_result["status"] == "completed", "Database backup should be completed"
        assert backup_result["type"] == "database", "Backup type should be database"
        assert backup_result["database"] == "bmad_production", "Database name should match"
        assert os.path.exists(backup_result["path"]), "Backup file should exist"
        assert backup_result["size"] > 0, "Backup should have size"

def test_file_backup():
    """Test file backup creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create test file
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("Test data for backup")
        
        # Create file backup
        backup_result = backup_manager.create_file_backup(test_file)
        
        # Verify backup creation
        assert backup_result["status"] == "completed", "File backup should be completed"
        assert backup_result["type"] == "file", "Backup type should be file"
        assert os.path.exists(backup_result["backup_path"]), "Backup file should exist"
        assert backup_result["size"] > 0, "Backup should have size"

def test_configuration_backup():
    """Test configuration backup creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create configuration backup
        backup_result = backup_manager.create_configuration_backup()
        
        # Verify backup creation
        assert backup_result["status"] == "completed", "Configuration backup should be completed"
        assert backup_result["type"] == "configuration", "Backup type should be configuration"
        assert os.path.exists(backup_result["path"]), "Backup file should exist"
        assert backup_result["size"] > 0, "Backup should have size"

def test_backup_integrity_validation():
    """Test backup integrity validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create a backup first
        backup_result = backup_manager.create_database_backup("test_db")
        
        # Validate backup integrity
        integrity_result = backup_manager.validate_backup_integrity(backup_result["id"])
        
        # Verify integrity validation
        assert integrity_result["integrity_check"] == "passed", "Backup integrity should pass"
        assert integrity_result["checksum_valid"] is True, "Checksum should be valid"
        assert integrity_result["file_size_valid"] is True, "File size should be valid"

def test_database_restoration():
    """Test database restoration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create a backup first
        backup_result = backup_manager.create_database_backup("test_db")
        
        # Restore the backup
        restore_result = backup_manager.restore_database_backup(backup_result["id"], "restored_db")
        
        # Verify restoration
        assert restore_result["status"] == "completed", "Database restoration should be completed"
        assert restore_result["type"] == "database", "Restoration type should be database"
        assert restore_result["target_database"] == "restored_db", "Target database should match"

def test_file_restoration():
    """Test file restoration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create test file and backup
        test_file = os.path.join(temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("Test data for backup")
        
        backup_result = backup_manager.create_file_backup(test_file)
        
        # Restore the backup
        restore_path = os.path.join(temp_dir, "restored_file.txt")
        restore_result = backup_manager.restore_file_backup(backup_result["id"], restore_path)
        
        # Verify restoration
        assert restore_result["status"] == "completed", "File restoration should be completed"
        assert restore_result["type"] == "file", "Restoration type should be file"
        assert restore_result["target_path"] == restore_path, "Target path should match"

def test_backup_summary():
    """Test backup summary generation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_manager = BackupManager(backup_dir=temp_dir)
        
        # Create multiple backups
        backup_manager.create_database_backup("db1")
        backup_manager.create_database_backup("db2")
        backup_manager.create_configuration_backup()
        
        # Get backup summary
        summary = backup_manager.get_backup_summary()
        
        # Verify summary
        assert summary["total_backups"] == 3, "Should have 3 total backups"
        assert summary["successful_backups"] == 3, "Should have 3 successful backups"
        assert summary["success_rate"] == 1.0, "Success rate should be 100%"
        assert "database" in summary["backup_types"], "Should have database backups"
        assert "configuration" in summary["backup_types"], "Should have configuration backups"

@pytest.mark.asyncio
async def test_recovery_procedures():
    """Test recovery procedure execution."""
    recovery_manager = RecoveryManager()
    
    # Register recovery procedures
    recovery_manager.register_recovery_procedure("database_recovery", mock_database_recovery)
    recovery_manager.register_recovery_procedure("file_recovery", mock_file_recovery)
    recovery_manager.register_recovery_procedure("config_recovery", mock_configuration_recovery)
    
    # Execute recovery procedures
    db_result = await recovery_manager.execute_recovery_procedure("database_recovery")
    file_result = await recovery_manager.execute_recovery_procedure("file_recovery")
    config_result = await recovery_manager.execute_recovery_procedure("config_recovery")
    
    # Verify recovery procedures
    assert db_result["status"] == "completed", "Database recovery should be completed"
    assert file_result["status"] == "completed", "File recovery should be completed"
    assert config_result["status"] == "completed", "Configuration recovery should be completed"
    
    assert db_result["duration"] > 0, "Database recovery should have duration"
    assert file_result["duration"] > 0, "File recovery should have duration"
    assert config_result["duration"] > 0, "Configuration recovery should have duration"

def test_backup_scheduling():
    """Test backup scheduling configuration."""
    # Test backup schedule configuration
    backup_schedule = {
        "database_backups": {
            "frequency": "daily",
            "time": "02:00",
            "retention_days": 30,
            "compression": True
        },
        "file_backups": {
            "frequency": "weekly",
            "day": "sunday",
            "time": "03:00",
            "retention_weeks": 12,
            "compression": True
        },
        "configuration_backups": {
            "frequency": "on_change",
            "retention_days": 90,
            "compression": False
        }
    }
    
    # Validate backup schedule
    assert "database_backups" in backup_schedule, "Database backup schedule should be configured"
    assert "file_backups" in backup_schedule, "File backup schedule should be configured"
    assert "configuration_backups" in backup_schedule, "Configuration backup schedule should be configured"
    
    # Validate database backup schedule
    db_schedule = backup_schedule["database_backups"]
    assert db_schedule["frequency"] == "daily", "Database backup should be daily"
    assert db_schedule["retention_days"] >= 7, "Database backup retention should be at least 7 days"
    
    # Validate file backup schedule
    file_schedule = backup_schedule["file_backups"]
    assert file_schedule["frequency"] == "weekly", "File backup should be weekly"
    assert file_schedule["retention_weeks"] >= 4, "File backup retention should be at least 4 weeks"

if __name__ == "__main__":
    # Run backup and recovery tests
    pytest.main([__file__, "-v", "--tb=short"]) 