"""S3 storage handler module."""
import os
from typing import Any, Dict, Optional
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from .base import StorageHandler

class S3StorageHandler(StorageHandler):
    """Handler for S3 storage."""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize S3 storage handler with settings."""
        super().__init__(settings)
        self.bucket_name = settings["bucket_name"]
        self.base_path = settings.get("base_path", "")
        
        # AWS credentials and region
        session_kwargs = {
            "aws_access_key_id": settings.get("aws_access_key_id"),
            "aws_secret_access_key": settings.get("aws_secret_access_key"),
        }
        
        if "aws_session_token" in settings:
            session_kwargs["aws_session_token"] = settings["aws_session_token"]
            
        if "region_name" in settings:
            session_kwargs["region_name"] = settings["region_name"]
            
        if "endpoint_url" in settings:
            # For using with S3-compatible storage (MinIO, etc.)
            session_kwargs["endpoint_url"] = settings["endpoint_url"]
        
        self.session = boto3.Session(**session_kwargs)
        self.s3 = self.session.client('s3')
    
    def _get_full_path(self, path: str) -> str:
        """Get full S3 path including base path."""
        if self.base_path:
            return f"{self.base_path.rstrip('/')}/{path}"
        return path
    
    async def test_connection(self) -> bool:
        """Test S3 connection and bucket access."""
        try:
            # Try to list objects with a limit of 1 to verify access
            self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            return True
        except ClientError:
            return False
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to S3 bucket."""
        try:
            self.s3.upload_file(
                local_path,
                self.bucket_name,
                self._get_full_path(remote_path)
            )
            return True
        except ClientError:
            return False
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from S3 bucket."""
        try:
            # Create local directories if needed
            os.makedirs(Path(local_path).parent, exist_ok=True)
            
            self.s3.download_file(
                self.bucket_name,
                self._get_full_path(remote_path),
                local_path
            )
            return True
        except ClientError:
            return False
    
    async def list_files(self, path: str) -> list[str]:
        """List files in S3 path."""
        try:
            full_path = self._get_full_path(path)
            prefix = f"{full_path}/" if full_path else ""
            
            paginator = self.s3.get_paginator('list_objects_v2')
            files = []
            
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Remove base_path from the key
                        key = obj['Key']
                        if self.base_path and key.startswith(self.base_path):
                            key = key[len(self.base_path.rstrip('/'))+1:]
                        files.append(key)
            
            return files
        except ClientError:
            return []
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from S3 bucket."""
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=self._get_full_path(path)
            )
            return True
        except ClientError:
            return False