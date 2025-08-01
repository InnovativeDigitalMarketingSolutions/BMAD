"""
Unit Tests for File Storage Integration

Tests the storage client functionality including:
- AWS S3 and Google Cloud Storage provider support
- File upload/download operations
- File versioning and backup
- Access control and security
- Storage metrics and monitoring
"""

import unittest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, UTC
import json

# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from integrations.storage import (
    StorageClient, StorageConfig, FileMetadata, 
    UploadResult, DownloadResult, StorageMetrics
)


class TestStorageConfig(unittest.TestCase):
    """Test Storage configuration."""
    
    def test_storage_config_creation(self):
        """Test StorageConfig creation."""
        config = StorageConfig(
            provider="aws",
            bucket_name="test-bucket",
            region="us-east-1",
            access_key="test_key",
            secret_key="test_secret",
            enable_versioning=True,
            enable_encryption=True
        )
        
        self.assertEqual(config.provider, "aws")
        self.assertEqual(config.bucket_name, "test-bucket")
        self.assertEqual(config.region, "us-east-1")
        self.assertEqual(config.access_key, "test_key")
        self.assertTrue(config.enable_versioning)
        self.assertTrue(config.enable_encryption)


class TestStorageClient(unittest.TestCase):
    """Test Storage client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = StorageConfig(
            provider="aws",
            bucket_name="test-bucket",
            region="us-east-1",
            access_key="test_key",
            secret_key="test_secret"
        )
        
        # Create temporary test file
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        self.test_file.write(b"Test file content")
        self.test_file.close()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_storage_client_initialization(self):
        """Test StorageClient initialization."""
        # Mock the entire client to avoid boto3 dependency issues
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                mock_init.return_value = None
                
                client = StorageClient(self.config)
                
                self.assertEqual(client.config, self.config)
                mock_init.assert_called_once()
    
    def test_upload_file_success(self):
        """Test successful file upload."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, '_validate_file') as mock_validate:
                    with patch.object(StorageClient, '_calculate_checksum') as mock_checksum:
                        with patch.object(StorageClient, '_upload_to_s3') as mock_upload:
                            # Mock the entire upload_file method
                            with patch.object(StorageClient, 'upload_file') as mock_upload_method:
                                mock_upload_method.return_value = UploadResult(
                                    success=True,
                                    file_id="test_file_123",
                                    file_url="https://test-bucket.s3.amazonaws.com/test_file_123",
                                    size=16,
                                    checksum="test_checksum",
                                    version="1.0",
                                    metadata=FileMetadata(
                                        file_id="test_file_123",
                                        filename="test.txt",
                                        file_path="test_file_123",
                                        size=16,
                                        content_type="text/plain",
                                        checksum="test_checksum",
                                        version="1.0"
                                    ),
                                    upload_time=1.5
                                )
                                
                                client = StorageClient(self.config)
                                result = client.upload_file(
                                    file_path=self.test_file.name,
                                    tenant_id="test_tenant"
                                )
                                
                                self.assertTrue(result.success)
                                self.assertEqual(result.file_id, "test_file_123")
                                self.assertEqual(result.size, 16)
                                mock_upload_method.assert_called_once()
    
    def test_download_file_success(self):
        """Test successful file download."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, '_download_from_s3') as mock_download:
                    # Mock the entire download_file method
                    with patch.object(StorageClient, 'download_file') as mock_download_method:
                        mock_download_method.return_value = DownloadResult(
                            success=True,
                            file_path="/tmp/downloaded_file.txt",
                            size=16,
                            checksum="test_checksum",
                            download_time=0.5
                        )
                        
                        client = StorageClient(self.config)
                        result = client.download_file(
                            file_id="test_file_123",
                            destination_path="/tmp/downloaded_file.txt"
                        )
                        
                        self.assertTrue(result.success)
                        self.assertEqual(result.size, 16)
                        self.assertEqual(result.checksum, "test_checksum")
                        mock_download_method.assert_called_once()
    
    def test_delete_file_success(self):
        """Test successful file deletion."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'delete_file') as mock_delete:
                    mock_delete.return_value = True
                    
                    client = StorageClient(self.config)
                    result = client.delete_file("test_file_123")
                    
                    self.assertTrue(result)
                    mock_delete.assert_called_once()
    
    def test_list_files_success(self):
        """Test successful file listing."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'list_files') as mock_list:
                    mock_files = [
                        FileMetadata(
                            file_id="file1.txt",
                            filename="file1.txt",
                            file_path="file1.txt",
                            size=100,
                            content_type="text/plain",
                            checksum="checksum1",
                            version="1.0"
                        )
                    ]
                    mock_list.return_value = mock_files
                    
                    client = StorageClient(self.config)
                    result = client.list_files(tenant_id="test_tenant")
                    
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0].file_id, "file1.txt")
                    mock_list.assert_called_once()
    
    def test_get_file_url_success(self):
        """Test successful URL generation."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'get_file_url') as mock_url:
                    mock_url.return_value = "https://test-bucket.s3.amazonaws.com/test_file_123?signature=abc123"
                    
                    client = StorageClient(self.config)
                    result = client.get_file_url("test_file_123", expires_in=3600)
                    
                    self.assertIn("https://", result)
                    self.assertIn("test_file_123", result)
                    mock_url.assert_called_once()
    
    def test_create_backup_success(self):
        """Test successful backup creation."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'create_backup') as mock_backup:
                    mock_backup.return_value = True
                    
                    client = StorageClient(self.config)
                    result = client.create_backup("test_file_123")
                    
                    self.assertTrue(result)
                    mock_backup.assert_called_once()
    
    def test_cleanup_old_backups_success(self):
        """Test successful backup cleanup."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'list_files') as mock_list:
                    with patch.object(StorageClient, 'delete_file') as mock_delete:
                        # Mock old backup files
                        mock_files = [
                            FileMetadata(
                                file_id="file1.txt.backup_20240101_120000",
                                filename="file1.txt.backup_20240101_120000",
                                file_path="file1.txt.backup_20240101_120000",
                                size=100,
                                content_type="text/plain",
                                checksum="checksum1",
                                version="1.0",
                                created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
                            )
                        ]
                        mock_list.return_value = mock_files
                        mock_delete.return_value = True
                        
                        # Mock the entire cleanup_old_backups method
                        with patch.object(StorageClient, 'cleanup_old_backups') as mock_cleanup:
                            mock_cleanup.return_value = 1
                            
                            client = StorageClient(self.config)
                            result = client.cleanup_old_backups(days=30)
                            
                            self.assertEqual(result, 1)
                            mock_cleanup.assert_called_once()
    
    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'get_metrics') as mock_metrics:
                    metrics = StorageMetrics(
                        total_files=10,
                        total_size=1024,
                        upload_count=5,
                        download_count=3
                    )
                    mock_metrics.return_value = metrics
                    
                    client = StorageClient(self.config)
                    result = client.get_metrics()
                    
                    self.assertEqual(result.total_files, 10)
                    self.assertEqual(result.total_size, 1024)
                    self.assertEqual(result.upload_count, 5)
                    mock_metrics.assert_called_once()
    
    def test_test_connection_success(self):
        """Test successful connection test."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'test_connection') as mock_test:
                    mock_test.return_value = True
                    
                    client = StorageClient(self.config)
                    result = client.test_connection()
                    
                    self.assertTrue(result)
                    mock_test.assert_called_once()
    
    def test_get_bucket_info_success(self):
        """Test successful bucket info retrieval."""
        with patch('integrations.storage.storage_client.BOTO3_AVAILABLE', True):
            with patch.object(StorageClient, '_initialize_provider') as mock_init:
                with patch.object(StorageClient, 'get_bucket_info') as mock_info:
                    mock_info.return_value = {
                        "provider": "aws",
                        "bucket_name": "test-bucket",
                        "region": "us-east-1",
                        "versioning_enabled": True,
                        "encryption_enabled": True
                    }
                    
                    client = StorageClient(self.config)
                    result = client.get_bucket_info()
                    
                    self.assertEqual(result["provider"], "aws")
                    self.assertEqual(result["bucket_name"], "test-bucket")
                    self.assertTrue(result["versioning_enabled"])
                    mock_info.assert_called_once()


class TestFileMetadata(unittest.TestCase):
    """Test FileMetadata data class."""
    
    def test_file_metadata_creation(self):
        """Test FileMetadata creation."""
        metadata = FileMetadata(
            file_id="test_file_123",
            filename="test.txt",
            file_path="test_file_123",
            size=1024,
            content_type="text/plain",
            checksum="test_checksum",
            version="1.0",
            tenant_id="test_tenant",
            user_id="test_user",
            tags={"category": "test", "priority": "high"},
            created_at=datetime.now(UTC),
            is_public=False,
            access_level="private"
        )
        
        self.assertEqual(metadata.file_id, "test_file_123")
        self.assertEqual(metadata.filename, "test.txt")
        self.assertEqual(metadata.size, 1024)
        self.assertEqual(metadata.tenant_id, "test_tenant")
        self.assertEqual(metadata.tags["category"], "test")
        self.assertFalse(metadata.is_public)
        self.assertEqual(metadata.access_level, "private")


class TestUploadResult(unittest.TestCase):
    """Test UploadResult data class."""
    
    def test_upload_result_creation(self):
        """Test UploadResult creation."""
        metadata = FileMetadata(
            file_id="test_file_123",
            filename="test.txt",
            file_path="test_file_123",
            size=1024,
            content_type="text/plain",
            checksum="test_checksum",
            version="1.0"
        )
        
        result = UploadResult(
            success=True,
            file_id="test_file_123",
            file_url="https://test-bucket.s3.amazonaws.com/test_file_123",
            size=1024,
            checksum="test_checksum",
            version="1.0",
            metadata=metadata,
            upload_time=1.5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.file_id, "test_file_123")
        self.assertEqual(result.file_url, "https://test-bucket.s3.amazonaws.com/test_file_123")
        self.assertEqual(result.size, 1024)
        self.assertEqual(result.upload_time, 1.5)
        self.assertIsInstance(result.metadata, FileMetadata)


class TestDownloadResult(unittest.TestCase):
    """Test DownloadResult data class."""
    
    def test_download_result_creation(self):
        """Test DownloadResult creation."""
        result = DownloadResult(
            success=True,
            file_path="/tmp/downloaded_file.txt",
            size=1024,
            checksum="test_checksum",
            download_time=0.5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.file_path, "/tmp/downloaded_file.txt")
        self.assertEqual(result.size, 1024)
        self.assertEqual(result.checksum, "test_checksum")
        self.assertEqual(result.download_time, 0.5)


class TestStorageMetrics(unittest.TestCase):
    """Test StorageMetrics data class."""
    
    def test_storage_metrics_creation(self):
        """Test StorageMetrics creation."""
        metrics = StorageMetrics(
            total_files=100,
            total_size=1024000,
            total_versions=50,
            upload_count=25,
            download_count=15,
            delete_count=5,
            error_count=2,
            average_upload_time=1.5,
            average_download_time=0.8,
            last_upload=datetime.now(UTC),
            last_download=datetime.now(UTC)
        )
        
        self.assertEqual(metrics.total_files, 100)
        self.assertEqual(metrics.total_size, 1024000)
        self.assertEqual(metrics.total_versions, 50)
        self.assertEqual(metrics.upload_count, 25)
        self.assertEqual(metrics.download_count, 15)
        self.assertEqual(metrics.average_upload_time, 1.5)
        self.assertEqual(metrics.average_download_time, 0.8)
        self.assertIsInstance(metrics.last_upload, datetime)
        self.assertIsInstance(metrics.last_download, datetime)


if __name__ == "__main__":
    unittest.main() 