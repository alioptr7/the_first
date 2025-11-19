"""
Users importer task for Request Network.

Reads exported JSON produced by Response Network (exports/users/latest.json or timestamped files)
and upserts users into the Request Network database. This task is safe to run repeatedly
-- it will update existing records and create missing ones. Password hashes are taken as-is
from the export (assumed to be bcrypt hashes produced by Response Network).

Security notes:
- Make sure exported files are transferred via a secure channel and checksummed in production.
- Do NOT use plaintext passwords in production exports.

"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from workers.celery_app import celery_app
from workers.database import db_session_scope

from api.models.user import User


# Allow pointing to Response Network exports in dev via env var
EXPORT_DIR = Path(os.getenv("RESPONSE_EXPORT_PATH", "./exports/users"))
LATEST_FILE = EXPORT_DIR / "latest.json"


def _select_export_file() -> Optional[Path]:
    """Return latest.json if present, otherwise the newest users_*.json file.

    EXPORT_DIR can point to Response Network exports in development (set RESPONSE_EXPORT_PATH).
    """
    if LATEST_FILE.exists():
        return LATEST_FILE

    if not EXPORT_DIR.exists():
        return None

    files = sorted(EXPORT_DIR.glob("users_*.json"), reverse=True)
    return files[0] if files else None


def import_users_sync(export_file: Optional[Path] = None) -> dict:
    """Synchronous importer helper. Returns a summary dict."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    file_path = export_file or _select_export_file()
    if not file_path or not file_path.exists():
        return {"status": "no_file", "imported": 0, "updated": 0}

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as e:
        return {"status": "error_reading_file", "error": str(e)}

    users = data.get("users", [])
    results = {"status": "ok", "imported": 0, "updated": 0, "errors": []}

    with db_session_scope() as db:
        for u in users:
            try:
                uid = uuid.UUID(u["id"]) if isinstance(u.get("id"), str) else u.get("id")
                existing = db.query(User).filter(User.id == uid).first()

                if existing:
                    existing.username = u.get("username", existing.username)
                    existing.email = u.get("email", existing.email)
                    existing.hashed_password = u.get("hashed_password", existing.hashed_password)
                    existing.full_name = u.get("full_name", existing.full_name)
                    existing.profile_type = u.get("role", existing.profile_type)
                    existing.is_active = u.get("is_active", existing.is_active)
                    existing.synced_at = datetime.utcnow()
                    db.add(existing)
                    results["updated"] += 1
                else:
                    new_user = User(
                        id=uid,
                        username=u.get("username"),
                        email=u.get("email"),
                        full_name=u.get("full_name"),
                        hashed_password=u.get("hashed_password") or "",
                        profile_type=u.get("role", "basic"),
                        is_active=u.get("is_active", True),
                        synced_at=datetime.utcnow(),
                    )
                    db.add(new_user)
                    results["imported"] += 1

            except Exception as exc:  # keep import robust
                results["errors"].append({
                    "user": u.get("id") if isinstance(u, dict) else str(u),
                    "error": str(exc),
                })

    return results


@celery_app.task(
    name="workers.tasks.users_importer.import_users_from_export",
    bind=True,
)
def import_users_from_export(self, export_file: Optional[str] = None):
    """Celery task wrapper that runs the synchronous importer.

    `export_file` is optional path to a specific export JSON for testing.
    """
    path = Path(export_file) if export_file else None
    res = import_users_sync(path)
    # If import was successful (no errors) and a concrete file was processed, delete it
    try:
        processed = path or _select_export_file()
        if processed and processed.exists():
            # consider success if res status ok and no errors or if exported count >0
            if res.get("status") in ("ok", "no_file"):
                # If there are errors, keep the file for inspection
                if not res.get("errors"):
                    try:
                        processed.unlink()
                    except Exception:
                        pass
    except Exception:
        pass

    return res
