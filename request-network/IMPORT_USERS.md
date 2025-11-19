# Users Importer (Request Network)

This document explains the new users importer which reads exported user JSON files
from the Response Network (placed under `request-network/exports/users/`) and upserts
them into the Request Network database.

Files expected:
- `request-network/exports/users/latest.json` preferred
- otherwise `request-network/exports/users/users_YYYYMMDD_HHMMSS.json`

Development tip: you can point the importer at the Response Network export directory by
setting the environment variable `RESPONSE_EXPORT_PATH` to the path of the exports
directory (for example: `..\response-network\api\exports\users`). In that case the
importer will read files from that location and, after a successful import, delete the
processed file.

Location of code:
- `request-network/workers/tasks/users_importer.py` (Celery task and sync helper)
- `request-network/api/scripts/run_users_importer.py` (run locally without Celery)

How it works:
- The importer reads the JSON file, iterates users and for each user either updates
  the existing read-replica row or inserts a new `users` row.
- Password hashes are consumed as-provided (assumed to be bcrypt hashes).

Run locally (no Celery):
```powershell
cd request-network/api
# Optionally set RESPONSE_EXPORT_PATH to point at response-network exports
$env:RESPONSE_EXPORT_PATH='C:\Users\win\the_first\response-network\api\exports\users'
python api/scripts/run_users_importer.py
```

Run as Celery task (if workers are running):
```powershell
# from the project root (example)
cd request-network
celery -A workers.celery_app call workers.tasks.users_importer.import_users_from_export
```

Security notes:
- Ensure exported files are moved securely and validated (checksums / signatures) before import.
- Do not export plaintext passwords. Use hashed passwords (bcrypt) or separate password-reset flow.
