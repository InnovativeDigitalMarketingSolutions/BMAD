"""
Storage Integration Client

This module provides the Storage client for the Integration Service,
handling file storage via AWS S3, Google Cloud Storage, and other providers.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime
import aiohttp
from pydantic import BaseModel
import json
import os

logger = logging.getLogger(__name__)

class FileInfo(BaseModel):
    key: str
    size: int
    last_modified: datetime
    content_type: Optional[str] = None
    etag: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class UploadResult(BaseModel):
    success: bool
    file_key: str
    url: Optional[str] = None
    size: int
    etag: Optional[str] = None
    error: Optional[str] = None

class DownloadResult(BaseModel):
    success: bool
    data: Optional[bytes] = None
    content_type: Optional[str] = None
    size: int
    error: Optional[str] = None

class StorageClient:
    """Storage client for file operations via AWS S3, GCS, etc."""
    
    def __init__(self, provider: str, credentials: Dict[str, str], bucket: str, 
                 region: Optional[str] = None):
        self.provider = provider.lower()
        self.credentials = credentials
        self.bucket = bucket
        self.region = region
        self.session: Optional[aiohttp.ClientSession] = None
        
        if self.provider == "aws":
            self.base_url = f"https://s3.{region}.amazonaws.com"
            self.headers = {
                "Authorization": self._get_aws_auth_header(),
                "Content-Type": "application/octet-stream"
            }
        elif self.provider == "gcs":
            self.base_url = f"https://storage.googleapis.com"
            self.headers = {
                "Authorization": f"Bearer {credentials.get('access_token')}",
                "Content-Type": "application/octet-stream"
            }
        else:
            raise ValueError(f"Unsupported storage provider: {provider}")
            
    def _get_aws_auth_header(self) -> str:
        """Generate AWS authentication header."""
        # Simplified AWS auth - in production use proper AWS SDK
        access_key = self.credentials.get("access_key_id")
        secret_key = self.credentials.get("secret_access_key")
        
        if not access_key or not secret_key:
            raise ValueError("AWS credentials not properly configured")
            
        # This is a simplified version - in production use proper AWS signature
        return f"AWS4-HMAC-SHA256 Credential={access_key}"
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def upload_file(self, file_key: str, data: bytes, 
                         content_type: Optional[str] = None,
                         metadata: Optional[Dict[str, str]] = None) -> UploadResult:
        """Upload a file to storage."""
        try:
            headers = self.headers.copy()
            if content_type:
                headers["Content-Type"] = content_type
                
            if metadata:
                for key, value in metadata.items():
                    headers[f"x-amz-meta-{key}"] = value
                    
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            else:
                return UploadResult(
                    success=False,
                    file_key=file_key,
                    size=len(data),
                    error=f"Unsupported provider: {self.provider}"
                )
                
            async with self.session.put(url, data=data, headers=headers) as response:
                if response.status in [200, 201]:
                    etag = response.headers.get("ETag", "").strip('"')
                    return UploadResult(
                        success=True,
                        file_key=file_key,
                        url=f"{self.base_url}/{self.bucket}/{file_key}",
                        size=len(data),
                        etag=etag
                    )
                else:
                    error_text = await response.text()
                    return UploadResult(
                        success=False,
                        file_key=file_key,
                        size=len(data),
                        error=f"Upload failed: {response.status} - {error_text}"
                    )
        except Exception as e:
            logger.error(f"Failed to upload file {file_key}: {e}")
            return UploadResult(
                success=False,
                file_key=file_key,
                size=len(data) if data else 0,
                error=str(e)
            )
            
    async def download_file(self, file_key: str) -> DownloadResult:
        """Download a file from storage."""
        try:
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            else:
                return DownloadResult(
                    success=False,
                    size=0,
                    error=f"Unsupported provider: {self.provider}"
                )
                
            async with self.session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.read()
                    content_type = response.headers.get("Content-Type")
                    return DownloadResult(
                        success=True,
                        data=data,
                        content_type=content_type,
                        size=len(data)
                    )
                else:
                    error_text = await response.text()
                    return DownloadResult(
                        success=False,
                        size=0,
                        error=f"Download failed: {response.status} - {error_text}"
                    )
        except Exception as e:
            logger.error(f"Failed to download file {file_key}: {e}")
            return DownloadResult(
                success=False,
                size=0,
                error=str(e)
            )
            
    async def delete_file(self, file_key: str) -> bool:
        """Delete a file from storage."""
        try:
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return False
                
            async with self.session.delete(url, headers=self.headers) as response:
                if response.status == 204:
                    logger.info(f"File deleted: {file_key}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Delete failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_key}: {e}")
            return False
            
    async def list_files(self, prefix: Optional[str] = None, 
                        max_keys: int = 1000) -> List[FileInfo]:
        """List files in storage."""
        try:
            params = {"list-type": "2", "max-keys": str(max_keys)}
            if prefix:
                params["prefix"] = prefix
                
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}"
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return []
                
            async with self.session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    # Parse XML response (simplified)
                    files = self._parse_list_response(xml_data)
                    return files
                else:
                    error_text = await response.text()
                    logger.error(f"List files failed: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
            
    def _parse_list_response(self, xml_data: str) -> List[FileInfo]:
        """Parse storage list response (simplified)."""
        # This is a simplified parser - in production use proper XML parsing
        files = []
        
        # Simple regex-like parsing for demonstration
        lines = xml_data.split('\n')
        for line in lines:
            if '<Key>' in line:
                key = line.split('<Key>')[1].split('</Key>')[0]
                size = 0
                last_modified = datetime.now()
                
                # Look for size and last modified in nearby lines
                for i, l in enumerate(lines):
                    if key in l:
                        if i + 1 < len(lines) and '<Size>' in lines[i + 1]:
                            size_str = lines[i + 1].split('<Size>')[1].split('</Size>')[0]
                            size = int(size_str)
                        if i + 2 < len(lines) and '<LastModified>' in lines[i + 2]:
                            date_str = lines[i + 2].split('<LastModified>')[1].split('</LastModified>')[0]
                            try:
                                last_modified = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            except:
                                pass
                        break
                        
                files.append(FileInfo(
                    key=key,
                    size=size,
                    last_modified=last_modified
                ))
                
        return files
        
    async def get_file_info(self, file_key: str) -> Optional[FileInfo]:
        """Get file information."""
        try:
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}/{file_key}"
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
                
            async with self.session.head(url, headers=self.headers) as response:
                if response.status == 200:
                    return FileInfo(
                        key=file_key,
                        size=int(response.headers.get("Content-Length", 0)),
                        last_modified=datetime.now(),  # Parse from response headers
                        content_type=response.headers.get("Content-Type"),
                        etag=response.headers.get("ETag", "").strip('"')
                    )
                else:
                    logger.error(f"Get file info failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Failed to get file info {file_key}: {e}")
            return None
            
    async def copy_file(self, source_key: str, destination_key: str) -> bool:
        """Copy a file within storage."""
        try:
            if self.provider == "aws":
                url = f"{self.base_url}/{self.bucket}/{destination_key}"
                headers = self.headers.copy()
                headers["x-amz-copy-source"] = f"/{self.bucket}/{source_key}"
            elif self.provider == "gcs":
                url = f"{self.base_url}/{self.bucket}/{destination_key}"
                headers = self.headers.copy()
                headers["x-goog-copy-source"] = f"/{self.bucket}/{source_key}"
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return False
                
            async with self.session.put(url, headers=headers) as response:
                if response.status in [200, 201]:
                    logger.info(f"File copied: {source_key} -> {destination_key}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Copy failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to copy file {source_key} -> {destination_key}: {e}")
            return False
            
    async def get_presigned_url(self, file_key: str, operation: str = "GET", 
                               expires_in: int = 3600) -> Optional[str]:
        """Get a presigned URL for file operations."""
        try:
            # This is a simplified implementation
            # In production, use proper AWS/GCS SDK for presigned URLs
            
            if self.provider == "aws":
                base_url = f"{self.base_url}/{self.bucket}/{file_key}"
                # Add query parameters for presigned URL
                params = {
                    "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
                    "X-Amz-Credential": self.credentials.get("access_key_id"),
                    "X-Amz-Date": datetime.now().strftime("%Y%m%dT%H%M%SZ"),
                    "X-Amz-Expires": str(expires_in),
                    "X-Amz-SignedHeaders": "host"
                }
                
                # Build query string
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                return f"{base_url}?{query_string}"
                
            elif self.provider == "gcs":
                base_url = f"{self.base_url}/{self.bucket}/{file_key}"
                # GCS presigned URL implementation
                params = {
                    "access_token": self.credentials.get("access_token"),
                    "expires": str(int(datetime.now().timestamp()) + expires_in)
                }
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                return f"{base_url}?{query_string}"
                
            else:
                logger.error(f"Presigned URLs not supported for provider: {self.provider}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {file_key}: {e}")
            return None
            
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            # List files to get basic stats
            files = await self.list_files(max_keys=1000)
            
            total_size = sum(file.size for file in files)
            total_files = len(files)
            
            # Group by content type
            content_types = {}
            for file in files:
                if file.content_type:
                    content_types[file.content_type] = content_types.get(file.content_type, 0) + 1
                    
            return {
                "provider": self.provider,
                "bucket": self.bucket,
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "content_types": content_types
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}
            
    async def health_check(self) -> Dict[str, Any]:
        """Check storage service health."""
        try:
            # Test by listing files
            files = await self.list_files(max_keys=1)
            
            # Get stats
            stats = await self.get_storage_stats()
            
            return {
                "status": "healthy",
                "provider": self.provider,
                "bucket": self.bucket,
                "region": self.region,
                "credentials_configured": bool(self.credentials),
                "storage_stats": stats
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider,
                "bucket": self.bucket,
                "credentials_configured": bool(self.credentials)
            } 