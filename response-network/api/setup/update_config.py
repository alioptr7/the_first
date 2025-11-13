"""
Update configuration dynamically without recreating .env.
Useful when Docker service addresses change.
"""
import sys
from pathlib import Path
from typing import Dict, Any
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def update_config(config_changes: Dict[str, Any]):
    """
    Update configuration with new values.
    
    Args:
        config_changes: Dictionary with configuration changes
        Example:
        {
            "REDIS_HOST": "redis-server",
            "REDIS_PORT": 6380,
            "DATABASE_CONFIG": {
                "RESPONSE_DB_HOST": "postgres-server"
            }
        }
    """
    from dotenv import set_key
    
    env_path = Path(__file__).parent.parent / ".env"
    
    print(f"🔄 Updating configuration at {env_path}\n")
    
    for key, value in config_changes.items():
        if isinstance(value, dict):
            # Nested configuration - flatten it
            for nested_key, nested_value in value.items():
                set_key(env_path, nested_key, str(nested_value))
                print(f"   {nested_key} = {nested_value}")
        else:
            set_key(env_path, key, str(value))
            print(f"   {key} = {value}")
    
    print(f"\n✅ Configuration updated successfully")


def get_current_config() -> Dict[str, Any]:
    """Get current configuration from .env file."""
    from dotenv import dotenv_values
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if not env_path.exists():
        print("⚠️  .env file not found")
        return {}
    
    config = dotenv_values(env_path)
    
    print("📋 Current Configuration:\n")
    for key, value in config.items():
        # Mask sensitive values
        if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY']):
            display_value = "*" * 8
        else:
            display_value = value
        
        print(f"   {key} = {display_value}")
    
    return config


def validate_config():
    """Validate that all required configuration is set."""
    from dotenv import dotenv_values
    
    env_path = Path(__file__).parent.parent / ".env"
    config = dotenv_values(env_path)
    
    required_keys = [
        "RESPONSE_DB_HOST",
        "RESPONSE_DB_PORT",
        "RESPONSE_DB_NAME",
        "REDIS_URL",
        "ELASTICSEARCH_URL",
    ]
    
    print("✅ Validating Configuration...\n")
    
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        print(f"❌ Missing required configuration:")
        for key in missing_keys:
            print(f"   - {key}")
        return False
    
    print("✅ All required configuration is present")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Response Network configuration")
    parser.add_argument("--show", action="store_true", help="Show current configuration")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--redis-host", type=str, help="Update Redis host")
    parser.add_argument("--redis-port", type=int, help="Update Redis port")
    parser.add_argument("--db-host", type=str, help="Update database host")
    parser.add_argument("--db-port", type=int, help="Update database port")
    parser.add_argument("--es-host", type=str, help="Update Elasticsearch host")
    parser.add_argument("--es-port", type=int, help="Update Elasticsearch port")
    
    args = parser.parse_args()
    
    if args.show:
        get_current_config()
    elif args.validate:
        validate_config()
    else:
        changes = {}
        
        if args.redis_host:
            changes["REDIS_URL"] = f"redis://{args.redis_host}:{args.redis_port or 6380}/0"
        if args.db_host:
            changes["RESPONSE_DB_HOST"] = args.db_host
        if args.db_port:
            changes["RESPONSE_DB_PORT"] = str(args.db_port)
        if args.es_host:
            changes["ELASTICSEARCH_URL"] = f"http://{args.es_host}:{args.es_port or 9200}"
        
        if changes:
            update_config(changes)
        else:
            parser.print_help()
