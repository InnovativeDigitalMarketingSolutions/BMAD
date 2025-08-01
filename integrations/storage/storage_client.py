"""
File Storage Integration Client

Provides comprehensive file storage integration for BMAD including:
- AWS S3 and Google Cloud Storage support
- File upload/download with progress tracking
- File versioning and metadata management
- Access control and security
- Backup strategies and CDN integration
- Multi-tenant file organization
"""

import os
import logging
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from pathlib import Path
from contextlib import contextmanager

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from google.cloud import storage
    from google.cloud.exceptions import GoogleCloudError
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class StorageConfig:
    """File storage configuration settings."""
    provider: str = "aws"  # "aws" or "gcp"
    bucket_name: Optional[str] = None
    region: str = "us-east-1"
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    google_credentials_path: Optional[str] = None
    google_project_id: Optional[str] = None
    enable_versioning: bool = True
    enable_encryption: bool = True
    enable_cdn: bool = False
    cdn_domain: Optional[str] = None
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = None
    backup_retention_days: int = 30
    compression_enabled: bool = False

@dataclass
class FileMetadata:
    """File metadata information."""
    file_id: str
    filename: str
    file_path: str
    size: int
    content_type: str
    checksum: str
    version: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: Dict[str, str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_public: bool = False
    access_level: str = "private"

@dataclass
class UploadResult:
    """File upload result."""
    success: bool
    file_id: str
    file_url: str
    size: int
    checksum: str
    version: str
    metadata: FileMetadata
    upload_time: float
    error_message: Optional[str] = None

@dataclass
class DownloadResult:
    """File download result."""
    success: bool
    file_path: str
    size: int
    checksum: str
    download_time: float
    error_message: Optional[str] = None

@dataclass
class StorageMetrics:
    """Storage usage metrics."""
    total_files: int = 0
    total_size: int = 0
    total_versions: int = 0
    upload_count: int = 0
    download_count: int = 0
    delete_count: int = 0
    error_count: int = 0
    average_upload_time: float = 0.0
    average_download_time: float = 0.0
    last_upload: Optional[datetime] = None
    last_download: Optional[datetime] = None

class StorageClient:
    """Comprehensive file storage client with multiple provider support."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.metrics = StorageMetrics()
        self._initialize_provider()
        logger.info(f"Storage client initialized with provider: {config.provider}")
    
    def _initialize_provider(self):
        """Initialize storage provider configuration."""
        if self.config.provider == "aws":
            if not BOTO3_AVAILABLE:
                raise ImportError("boto3 is required for AWS S3 integration. Install with: pip install boto3")
            
            if not self.config.bucket_name:
                self.config.bucket_name = os.getenv("AWS_S3_BUCKET")
            if not self.config.access_key:
                self.config.access_key = os.getenv("AWS_ACCESS_KEY_ID")
            if not self.config.secret_key:
                self.config.secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            if not self.config.region:
                self.config.region = os.getenv("AWS_REGION", "us-east-1")
            
            if not self.config.bucket_name:
                raise ValueError("AWS S3 bucket name required")
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region
            )
            
        elif self.config.provider == "gcp":
            if not GOOGLE_CLOUD_AVAILABLE:
                raise ImportError("google-cloud-storage is required for GCP integration. Install with: pip install google-cloud-storage")
            
            if not self.config.bucket_name:
                self.config.bucket_name = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
            if not self.config.google_project_id:
                self.config.google_project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if not self.config.google_credentials_path:
                self.config.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if not self.config.bucket_name:
                raise ValueError("Google Cloud Storage bucket name required")
            
            if self.config.google_credentials_path:
                self.gcp_client = storage.Client.from_service_account_json(
                    self.config.google_credentials_path
                )
            else:
                self.gcp_client = storage.Client(project=self.config.google_project_id)
            
            self.bucket = self.gcp_client.bucket(self.config.bucket_name)
        else:
            raise ValueError(f"Unsupported storage provider: {self.config.provider}")
    
    def _generate_file_id(self, filename: str, tenant_id: Optional[str] = None) -> str:
        """Generate a unique file ID."""
        timestamp = datetime.now(UTC).isoformat()
        file_hash = hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()
        
        if tenant_id:
            return f"{tenant_id}/{file_hash}/{filename}"
        return f"{file_hash}/{filename}"
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _validate_file(self, file_path: str) -> bool:
        """Validate file before upload."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size > self.config.max_file_size:
            raise ValueError(f"File size {file_size} exceeds maximum {self.config.max_file_size}")
        
        if self.config.allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.config.allowed_extensions:
                raise ValueError(f"File extension {file_ext} not allowed")
        
        return True
    
    # File Upload Operations
    def upload_file(self, file_path: str, destination_path: Optional[str] = None,
                   tenant_id: Optional[str] = None, user_id: Optional[str] = None,
                   tags: Optional[Dict[str, str]] = None, is_public: bool = False,
                   content_type: Optional[str] = None) -> UploadResult:
        """Upload a file to storage."""
        start_time = time.time()
        
        try:
            # Validate file
            self._validate_file(file_path)
            
            # Generate file ID and path
            filename = os.path.basename(file_path)
            file_id = self._generate_file_id(filename, tenant_id)
            storage_path = destination_path or file_id
            
            # Calculate checksum
            checksum = self._calculate_checksum(file_path)
            
            # Upload based on provider
            if self.config.provider == "aws":
                result = self._upload_to_s3(file_path, storage_path, content_type, tags, is_public)
            elif self.config.provider == "gcp":
                result = self._upload_to_gcp(file_path, storage_path, content_type, tags, is_public)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            # Create metadata
            metadata = FileMetadata(
                file_id=file_id,
                filename=filename,
                file_path=storage_path,
                size=os.path.getsize(file_path),
                content_type=content_type or "application/octet-stream",
                checksum=checksum,
                version="1.0",
                tenant_id=tenant_id,
                user_id=user_id,
                tags=tags or {},
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                is_public=is_public,
                access_level="public" if is_public else "private"
            )
            
            upload_time = time.time() - start_time
            
            # Update metrics
            self.metrics.upload_count += 1
            self.metrics.total_files += 1
            self.metrics.total_size += metadata.size
            self.metrics.average_upload_time = (
                (self.metrics.average_upload_time * (self.metrics.upload_count - 1) + upload_time) 
                / self.metrics.upload_count
            )
            self.metrics.last_upload = datetime.now(UTC)
            
            return UploadResult(
                success=True,
                file_id=file_id,
                file_url=result["url"],
                size=metadata.size,
                checksum=checksum,
                version=metadata.version,
                metadata=metadata,
                upload_time=upload_time
            )
            
        except Exception as e:
            upload_time = time.time() - start_time
            self.metrics.error_count += 1
            logger.error(f"File upload failed: {e}")
            
            return UploadResult(
                success=False,
                file_id="",
                file_url="",
                size=0,
                checksum="",
                version="",
                metadata=None,
                upload_time=upload_time,
                error_message=str(e)
            )
    
    def _upload_to_s3(self, file_path: str, storage_path: str, content_type: str,
                     tags: Optional[Dict[str, str]], is_public: bool) -> Dict[str, Any]:
        """Upload file to AWS S3."""
        try:
            extra_args = {
                'ContentType': content_type or 'application/octet-stream'
            }
            
            if self.config.enable_encryption:
                extra_args['ServerSideEncryption'] = 'AES256'
            
            if tags:
                extra_args['Tagging'] = '&'.join([f"{k}={v}" for k, v in tags.items()])
            
            if is_public:
                extra_args['ACL'] = 'public-read'
            
            self.s3_client.upload_file(file_path, self.config.bucket_name, storage_path, ExtraArgs=extra_args)
            
            url = f"https://{self.config.bucket_name}.s3.{self.config.region}.amazonaws.com/{storage_path}"
            if self.config.enable_cdn and self.config.cdn_domain:
                url = f"https://{self.config.cdn_domain}/{storage_path}"
            
            return {"url": url}
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    def _upload_to_gcp(self, file_path: str, storage_path: str, content_type: str,
                      tags: Optional[Dict[str, str]], is_public: bool) -> Dict[str, Any]:
        """Upload file to Google Cloud Storage."""
        try:
            blob = self.bucket.blob(storage_path)
            
            if content_type:
                blob.content_type = content_type
            
            if tags:
                blob.metadata = tags
            
            if is_public:
                blob.make_public()
            
            blob.upload_from_filename(file_path)
            
            url = blob.public_url if is_public else blob.self_link
            if self.config.enable_cdn and self.config.cdn_domain:
                url = f"https://{self.config.cdn_domain}/{storage_path}"
            
            return {"url": url}
            
        except Exception as e:
            logger.error(f"GCP upload failed: {e}")
            raise
    
    # File Download Operations
    def download_file(self, file_id: str, destination_path: str) -> DownloadResult:
        """Download a file from storage."""
        start_time = time.time()
        
        try:
            if self.config.provider == "aws":
                result = self._download_from_s3(file_id, destination_path)
            elif self.config.provider == "gcp":
                result = self._download_from_gcp(file_id, destination_path)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            download_time = time.time() - start_time
            file_size = os.path.getsize(destination_path)
            checksum = self._calculate_checksum(destination_path)
            
            # Update metrics
            self.metrics.download_count += 1
            self.metrics.average_download_time = (
                (self.metrics.average_download_time * (self.metrics.download_count - 1) + download_time) 
                / self.metrics.download_count
            )
            self.metrics.last_download = datetime.now(UTC)
            
            return DownloadResult(
                success=True,
                file_path=destination_path,
                size=file_size,
                checksum=checksum,
                download_time=download_time
            )
            
        except Exception as e:
            download_time = time.time() - start_time
            self.metrics.error_count += 1
            logger.error(f"File download failed: {e}")
            
            return DownloadResult(
                success=False,
                file_path="",
                size=0,
                checksum="",
                download_time=download_time,
                error_message=str(e)
            )
    
    def _download_from_s3(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Download file from AWS S3."""
        try:
            self.s3_client.download_file(self.config.bucket_name, file_id, destination_path)
            return {"success": True}
        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            raise
    
    def _download_from_gcp(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Download file from Google Cloud Storage."""
        try:
            blob = self.bucket.blob(file_id)
            blob.download_to_filename(destination_path)
            return {"success": True}
        except Exception as e:
            logger.error(f"GCP download failed: {e}")
            raise
    
    # File Management Operations
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from storage."""
        try:
            if self.config.provider == "aws":
                self.s3_client.delete_object(Bucket=self.config.bucket_name, Key=file_id)
            elif self.config.provider == "gcp":
                blob = self.bucket.blob(file_id)
                blob.delete()
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            self.metrics.delete_count += 1
            logger.info(f"File deleted: {file_id}")
            return True
            
        except Exception as e:
            self.metrics.error_count += 1
            logger.error(f"File deletion failed: {e}")
            return False
    
    def list_files(self, prefix: Optional[str] = None, tenant_id: Optional[str] = None) -> List[FileMetadata]:
        """List files in storage."""
        try:
            files = []
            
            if self.config.provider == "aws":
                response = self.s3_client.list_objects_v2(
                    Bucket=self.config.bucket_name,
                    Prefix=prefix or (f"{tenant_id}/" if tenant_id else "")
                )
                
                for obj in response.get('Contents', []):
                    metadata = FileMetadata(
                        file_id=obj['Key'],
                        filename=os.path.basename(obj['Key']),
                        file_path=obj['Key'],
                        size=obj['Size'],
                        content_type="application/octet-stream",
                        checksum=obj.get('ETag', '').strip('"'),
                        version="1.0",
                        created_at=obj['LastModified'],
                        updated_at=obj['LastModified']
                    )
                    files.append(metadata)
                    
            elif self.config.provider == "gcp":
                blobs = self.bucket.list_blobs(prefix=prefix or (f"{tenant_id}/" if tenant_id else ""))
                
                for blob in blobs:
                    metadata = FileMetadata(
                        file_id=blob.name,
                        filename=os.path.basename(blob.name),
                        file_path=blob.name,
                        size=blob.size,
                        content_type=blob.content_type or "application/octet-stream",
                        checksum=blob.md5_hash,
                        version="1.0",
                        created_at=blob.time_created,
                        updated_at=blob.updated
                    )
                    files.append(metadata)
            
            return files
            
        except Exception as e:
            logger.error(f"File listing failed: {e}")
            return []
    
    def get_file_url(self, file_id: str, expires_in: int = 3600) -> str:
        """Get a signed URL for file access."""
        try:
            if self.config.provider == "aws":
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.config.bucket_name, 'Key': file_id},
                    ExpiresIn=expires_in
                )
            elif self.config.provider == "gcp":
                blob = self.bucket.blob(file_id)
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.now(UTC) + timedelta(seconds=expires_in)
                )
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            return url
            
        except Exception as e:
            logger.error(f"URL generation failed: {e}")
            return ""
    
    # Backup and Versioning Operations
    def create_backup(self, file_id: str) -> bool:
        """Create a backup version of a file."""
        try:
            if not self.config.enable_versioning:
                logger.warning("Versioning not enabled")
                return False
            
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_id = f"{file_id}.backup_{timestamp}"
            
            if self.config.provider == "aws":
                self.s3_client.copy_object(
                    Bucket=self.config.bucket_name,
                    CopySource={'Bucket': self.config.bucket_name, 'Key': file_id},
                    Key=backup_id
                )
            elif self.config.provider == "gcp":
                source_blob = self.bucket.blob(file_id)
                backup_blob = self.bucket.blob(backup_id)
                self.bucket.copy_blob(source_blob, self.bucket, backup_blob.name)
            
            self.metrics.total_versions += 1
            logger.info(f"Backup created: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def cleanup_old_backups(self, days: Optional[int] = None) -> int:
        """Clean up old backup files."""
        try:
            retention_days = days or self.config.backup_retention_days
            cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)
            deleted_count = 0
            
            files = self.list_files()
            for file_metadata in files:
                if file_metadata.file_path.endswith('.backup_'):
                    if file_metadata.created_at and file_metadata.created_at < cutoff_date:
                        if self.delete_file(file_metadata.file_id):
                            deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return 0
    
    # Utility Methods
    def get_metrics(self) -> StorageMetrics:
        """Get storage usage metrics."""
        return self.metrics
    
    def test_connection(self) -> bool:
        """Test storage connection."""
        try:
            if self.config.provider == "aws":
                self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            elif self.config.provider == "gcp":
                self.bucket.reload()
            
            logger.info(f"Storage connection test successful for {self.config.provider}")
            return True
            
        except Exception as e:
            logger.error(f"Storage connection test failed: {e}")
            return False
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """Get bucket information."""
        try:
            if self.config.provider == "aws":
                response = self.s3_client.head_bucket(Bucket=self.config.bucket_name)
                return {
                    "provider": "aws",
                    "bucket_name": self.config.bucket_name,
                    "region": self.config.region,
                    "versioning_enabled": self.config.enable_versioning,
                    "encryption_enabled": self.config.enable_encryption
                }
            elif self.config.provider == "gcp":
                self.bucket.reload()
                return {
                    "provider": "gcp",
                    "bucket_name": self.config.bucket_name,
                    "project_id": self.config.google_project_id,
                    "versioning_enabled": self.config.enable_versioning,
                    "encryption_enabled": self.config.enable_encryption
                }
            
        except Exception as e:
            logger.error(f"Failed to get bucket info: {e}")
            return {} 