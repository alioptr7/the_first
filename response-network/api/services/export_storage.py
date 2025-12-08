"""
Storage service for handling file exports to different destinations.
"""
from pathlib import Path
from typing import BinaryIO, Union
import tempfile

from core.config import settings
from storage.local import LocalStorageHandler
from storage.ftp import FTPStorageHandler


class ExportStorageService:
    """Service for saving export files to configured destination."""
    
    @staticmethod
    async def save_export_file(filename: str, data: bytes) -> str:
        """
        Save export file to configured destination.
        
        Args:
            filename: Name of the file to save
            data: File content as bytes
            
        Returns:
            Path or URL where file was saved
        """
        if settings.EXPORT_DESTINATION_TYPE == "ftp":
            return await ExportStorageService._save_to_ftp(filename, data)
        else:
            return await ExportStorageService._save_to_local(filename, data)
    
    @staticmethod
    async def _save_to_local(filename: str, data: bytes) -> str:
        """Save file to local file system."""
        handler = LocalStorageHandler({"base_path": settings.EXPORT_DIR})
        
        # Write to temp file first
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        
        # Upload (copy) to destination
        await handler.upload_file(tmp_path, filename)
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
        return str(Path(settings.EXPORT_DIR) / filename)
    
    @staticmethod
    async def _save_to_ftp(filename: str, data: bytes) -> str:
        """Save file to FTP server."""
        ftp_settings = {
            "host": settings.EXPORT_FTP_HOST,
            "port": settings.EXPORT_FTP_PORT,
            "username": settings.EXPORT_FTP_USERNAME,
            "password": settings.EXPORT_FTP_PASSWORD,
            "base_path": settings.EXPORT_FTP_PATH,
            "use_tls": settings.EXPORT_FTP_USE_TLS,
        }
        
        handler = FTPStorageHandler(ftp_settings)
        
        # Write to temp file first
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        
        # Upload to FTP
        await handler.upload_file(tmp_path, filename)
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
        return f"ftp://{settings.EXPORT_FTP_HOST}{settings.EXPORT_FTP_PATH}/{filename}"
