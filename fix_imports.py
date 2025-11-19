
import os
import glob

def replace_in_file(file_path, old_str, new_str):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_str, new_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    for filepath in glob.iglob('c:/Users/win/the_first/response-network/api/**/*.py', recursive=True):
        replace_in_file(filepath, 'from core.dependencies import get_db', 'from db.session import get_db_session as get_db')
        replace_in_file(filepath, 'from core.dependencies import get_db_sync', 'from db.session import get_db_session as get_db_sync')
        replace_in_file(filepath, 'from core.dependencies import get_current_superuser, get_db', 'from auth.dependencies import get_current_active_user as get_current_superuser\nfrom db.session import get_db_session as get_db')
        replace_in_file(filepath, 'from core.dependencies import get_db, get_redis', 'from db.session import get_db_session as get_db\nfrom workers.redis_client import get_redis')

if __name__ == "__main__":
    main()
