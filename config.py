import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'log_paths': ['/var/log/auth.log', '/var/log/secure'],
    'thresholds': {
        'info': 1,
        'warning': 3,
        'critical': 5
    },
    'reset_after': 86400,      # 24 hours
    'alert_cooldown': 300,     # 5 minutes
    'state_file': 'sentinelx_state.json',
    'run_as_user': 'nobody',
    'run_as_group': 'nogroup',
    'output_format': {
        'icons': {
            'info': '[  INFO  ]',
            'warning': '[WARNING ]',
            'critical': '[CRITICAL]'
        },
        'column_widths': {
            'ip': 16,
            'username': 12
        },
        'date_format': ''  # empty means keep original log timestamp
    }
}

def validate_config(config: dict):
    """Validate configuration parameters."""
    if not isinstance(config.get('log_paths'), list) or not all(isinstance(p, str) for p in config['log_paths']):
        raise ValueError("config 'log_paths' must be a list of strings")

    thresholds = config.get('thresholds')
    if not isinstance(thresholds, dict):
        raise ValueError("config 'thresholds' must be a dictionary")
    
    for level in ['info', 'warning', 'critical']:
        if level not in thresholds:
            raise ValueError(f"config 'thresholds' is missing level: {level}")
        val = thresholds[level]
        if not isinstance(val, int) or val <= 0:
            raise ValueError(f"threshold value for {level} must be a positive integer")

    if thresholds['info'] > thresholds['warning'] or thresholds['warning'] > thresholds['critical']:
        raise ValueError("thresholds must satisfy: info <= warning <= critical")

    for key in ['reset_after', 'alert_cooldown']:
        val = config.get(key)
        if not isinstance(val, (int, float)) or val < 0:
            raise ValueError(f"{key} must be a non-negative number")

    if 'state_file' in config and config['state_file'] is not None:
        if not isinstance(config['state_file'], str):
            raise ValueError("state_file must be a string path")

def load_config(config_path='config.yaml') -> dict:
    """
    Load configuration. Merges defaults, YAML configuration, and environment variables.
    """
    config = dict(DEFAULT_CONFIG)

    # 1. Load from YAML file if exists
    config_path = Path(config_path)
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
            if user_config and isinstance(user_config, dict):
                # Deep merge thresholds and output_format
                for key, value in user_config.items():
                    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                        config[key] = {**config[key], **value}
                    else:
                        config[key] = value
        except Exception as e:
            logger.error(f"Failed to load config file {config_path}: {e}")

    # 2. Override from environment variables
    # SENTINELX_LOG_PATHS (comma-separated list)
    env_paths = os.environ.get("SENTINELX_LOG_PATHS")
    if env_paths:
        config['log_paths'] = [p.strip() for p in env_paths.split(',') if p.strip()]

    # SENTINELX_THRESHOLDS_INFO, etc.
    for level in ['info', 'warning', 'critical']:
        env_val = os.environ.get(f"SENTINELX_THRESHOLDS_{level.upper()}")
        if env_val:
            try:
                config['thresholds'][level] = int(env_val)
            except ValueError:
                logger.warning(f"Invalid env value for SENTINELX_THRESHOLDS_{level.upper()}: {env_val}")

    # SENTINELX_RESET_AFTER
    env_reset = os.environ.get("SENTINELX_RESET_AFTER")
    if env_reset:
        try:
            config['reset_after'] = int(env_reset)
        except ValueError:
            logger.warning(f"Invalid env value for SENTINELX_RESET_AFTER: {env_reset}")

    # SENTINELX_ALERT_COOLDOWN
    env_cooldown = os.environ.get("SENTINELX_ALERT_COOLDOWN")
    if env_cooldown:
        try:
            config['alert_cooldown'] = int(env_cooldown)
        except ValueError:
            logger.warning(f"Invalid env value for SENTINELX_ALERT_COOLDOWN: {env_cooldown}")

    # SENTINELX_STATE_FILE
    env_state = os.environ.get("SENTINELX_STATE_FILE")
    if env_state:
        config['state_file'] = env_state

    # SENTINELX_RUN_AS_USER / GROUP
    env_user = os.environ.get("SENTINELX_RUN_AS_USER")
    if env_user:
        config['run_as_user'] = env_user
    env_group = os.environ.get("SENTINELX_RUN_AS_GROUP")
    if env_group:
        config['run_as_group'] = env_group

    # Validate the final config
    validate_config(config)

    return config