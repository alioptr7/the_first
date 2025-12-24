import os
import json
import logging
import ftplib
import io
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.settings import Settings

logger = logging.getLogger(__name__)

class ImportStorageService:
    @staticmethod
    def get_import_config(db: Session) -> dict:
        """Fetch import configuration from database settings."""
        result = db.execute(select(Settings).where(Settings.key == "import_config"))
        setting = result.scalar_one_or_none()
        if not setting or not setting.value:
            return None
        return setting.value

    @staticmethod
    def read_latest_file(db: Session, resource_type: str) -> dict:
        """
        Read the latest import file for a resource type (e.g., 'users').
        Abstraacts away Local vs FTP logic.
        """
        config = ImportStorageService.get_import_config(db)
        if not config:
            logger.warning(f"Skipping import for {resource_type}: 'import_config' not set.")
            return None

        import_type = config.get("type", "local")
        
        if import_type == "local":
            base_path = Path(config.get("path", "/app/imports"))
            file_path = base_path / resource_type / "latest.json"
            
            if not file_path.exists():
                logger.info(f"No import file found at {file_path}")
                return None
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read local import file {file_path}: {e}")
                return None
        
        elif import_type == "ftp":
            host = config.get("host")
            user = config.get("user")
            passwd = config.get("password")
            remote_path = config.get("path", f"/{resource_type}")
            
            if not host:
                logger.error(f"FTP host missing in import_config for {resource_type}")
                return None
            
            try:
                bio = io.BytesIO()
                with ftplib.FTP(host) as ftp:
                    ftp.login(user=user, passwd=passwd)
                    try:
                        ftp.cwd(remote_path)
                    except:
                        pass
                    
                    ftp.retrbinary(f"RETR latest.json", bio.write)
                
                bio.seek(0)
                return json.load(bio)
            except Exception as e:
                logger.error(f"FTP Download failed from {host}:{remote_path}: {e}")
                return None
        
        else:
            logger.error(f"Unknown import type: {import_type}")
            return None
