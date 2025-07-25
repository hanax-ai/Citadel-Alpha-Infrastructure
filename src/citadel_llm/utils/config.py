import os
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def load_config(env: str = None) -> Dict[str, Any]:
    """
    Loads the complete application configuration from YAML files.
    Order of loading: global -> service-specific -> environment-specific -> secrets.
    """
    config = {}
    citadel_home = os.environ.get('CITADEL_HOME', '/opt/citadel-02')
    if not citadel_home:
        logger.error("CITADEL_HOME environment variable not set.")
        raise EnvironmentError("CITADEL_HOME environment variable not set.")

    config_base_path = os.path.join(citadel_home, 'config')

    # 1. Load global configurations
    global_config_path = os.path.join(config_base_path, 'global')
    if os.path.exists(global_config_path):
        for filename in os.listdir(global_config_path):
            if filename.endswith('.yaml'):
                try:
                    with open(os.path.join(global_config_path, filename), 'r') as f:
                        global_data = yaml.safe_load(f)
                        if global_data:
                            config.update(global_data)
                except Exception as e:
                    logger.warning(f"Failed to load global config {filename}: {e}")
        logger.info(f"Loaded global configurations from {global_config_path}")

    # 2. Load service-specific configurations
    services_config_path = os.path.join(config_base_path, 'services')
    if os.path.exists(services_config_path):
        for service_dir in os.listdir(services_config_path):
            service_path = os.path.join(services_config_path, service_dir)
            if os.path.isdir(service_path):
                for filename in os.listdir(service_path):
                    if filename.endswith('.yaml'):
                        try:
                            with open(os.path.join(service_path, filename), 'r') as f:
                                service_data = yaml.safe_load(f)
                                if service_data:
                                    # Merge service config under its own key, e.g., config['ollama']
                                    service_name = service_dir.replace('-', '_') # api-gateway -> api_gateway
                                    if service_name not in config:
                                        config[service_name] = {}
                                    config[service_name].update(service_data)
                        except Exception as e:
                            logger.warning(f"Failed to load service config {service_dir}/{filename}: {e}")
        logger.info(f"Loaded service configurations from {services_config_path}")

    # 3. Load environment-specific configurations
    current_env = env if env else os.environ.get('CITADEL_ENV', 'development')
    env_config_file = os.path.join(config_base_path, 'environments', f'{current_env}.yaml')
    if os.path.exists(env_config_file):
        try:
            with open(env_config_file, 'r') as f:
                env_config = yaml.safe_load(f)
                if env_config:
                    # Merge environment-specific configs, potentially overriding global/service settings
                    _deep_merge_dicts(config, env_config)
            logger.info(f"Loaded environment-specific configurations from {env_config_file}")
        except Exception as e:
            logger.warning(f"Failed to load environment config {env_config_file}: {e}")
    else:
        logger.warning(f"Environment configuration file not found: {env_config_file}")

    # 4. Load secrets
    secrets_path = os.path.join(config_base_path, 'secrets')
    if os.path.exists(secrets_path):
        for filename in os.listdir(secrets_path):
            if filename.endswith('.yaml'):
                filepath = os.path.join(secrets_path, filename)
                try:
                    # Ensure secrets files are only readable by owner
                    file_mode = oct(os.stat(filepath).st_mode & 0o777)
                    if file_mode not in ['0o600', '0o400']:
                        logger.warning(f"Insecure permissions for secret file: {filepath}. Expected 600 or 400, got {file_mode}")
                    
                    with open(filepath, 'r') as f:
                        secrets = yaml.safe_load(f)
                        if secrets: # Ensure secrets is not None if file is empty
                            # Merge secrets directly at the top level
                            config.update(secrets)
                except Exception as e:
                    logger.warning(f"Failed to load secrets from {filepath}: {e}")
        logger.info(f"Loaded secrets from {secrets_path}")

    return config

def _deep_merge_dicts(d1: Dict, d2: Dict):
    """Recursively merges dictionary d2 into d1."""
    for k, v in d2.items():
        if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
            _deep_merge_dicts(d1[k], v)
        else:
            d1[k] = v

def get_database_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract database configuration from loaded config"""
    db_config = {}
    
    # Get database config from integration services
    integration_config = config.get('integration', {})
    if 'database' in integration_config:
        db_config.update(integration_config['database'])
    
    # Get credentials from database section
    database_creds = config.get('database', {})
    if database_creds:
        db_config.update(database_creds)
    
    return db_config

if __name__ == '__main__':
    # This block is for testing the config loader
    try:
        # Set CITADEL_HOME for testing purposes if not already set
        if 'CITADEL_HOME' not in os.environ:
            os.environ['CITADEL_HOME'] = '/opt/citadel'
        # Set CITADEL_ENV for testing purposes
        if 'CITADEL_ENV' not in os.environ:
            os.environ['CITADEL_ENV'] = 'development'

        # Configure logging for testing
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        app_config = load_config()
        import json
        print("=== LOADED CONFIGURATION ===")
        print(json.dumps(app_config, indent=2, default=str))

        # Test access to some specific values
        print(f"\n=== KEY CONFIGURATION VALUES ===")
        print(f"Project Name: {app_config.get('project', {}).get('name', 'Not found')}")
        print(f"API Gateway Port: {app_config.get('api_gateway', {}).get('port', 'Not found')}")
        print(f"Ollama Model Dir: {app_config.get('ollama', {}).get('model_dir', 'Not found')}")
        
        # Database configuration
        db_config = get_database_config(app_config)
        print(f"Database Host: {db_config.get('host', 'Not found')}")
        print(f"Database Port: {db_config.get('port', 'Not found')}")
        print(f"Database Name: {db_config.get('database', 'Not found')}")
        print(f"Database User: {db_config.get('username', 'Not found')}")
        print(f"Database Password: {'***REDACTED***' if db_config.get('password') else 'Not found'}")

    except Exception as e:
        logger.exception("Error loading configuration:")
        import sys
        sys.exit(1)
