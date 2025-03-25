"""Configuration management for SMTP2GO Usage Reporter.

This module handles loading and validating configuration settings.
"""
import os
import json
import logging
import argparse
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the application."""
    
    # Default config path (kept for backwards compatibility)
    DEFAULT_CONFIG_PATH = os.path.expanduser("~/.smtp2go-usage/config.json")
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.config = {
            # API Settings
            "api_key": None,
            
            # SMTP Settings (for sending reports)
            "smtp_server": "smtp2go.com",
            "smtp_port": 587,
            "smtp_username": None,
            "smtp_password": None,
            "sender_email": None,
            
            # Report Settings
            "report_recipients": [],
            "report_subject_template": "SMTP2GO Usage Report - {period}",
            "report_dir": os.path.expanduser("~/smtp2go-reports")
        }
    
    def load_from_file(self, config_file=None):
        """DEPRECATED: Load configuration from a JSON file.
        
        This method is kept for backward compatibility but is no longer recommended.
        Please use environment variables instead.
        
        Args:
            config_file (str, optional): Path to the configuration file
                
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        if not config_file:
            logger.info("No config file specified. Using environment variables instead.")
            return False
            
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                
            # Update config with loaded values
            self.config.update(loaded_config)
            logger.info(f"Configuration loaded from {config_file}")
            return True
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_file}")
            return False
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_file}")
            return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save_to_file(self, config_file=None):
        """Save current configuration to a JSON file.
        
        Args:
            config_file (str, optional): Path to save the configuration to
                If not provided, uses the default path
                
        Returns:
            bool: True if configuration was saved successfully, False otherwise
        """
        file_path = config_file or self.DEFAULT_CONFIG_PATH
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
            logger.info(f"Configuration saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def update_from_env(self):
        """Update configuration from environment variables.
        
        Environment variables take precedence over configuration file values.
        
        Returns:
            bool: True if any configuration was updated, False otherwise
        """
        updated = False
        
        # Mapping of environment variables to config keys
        env_mapping = {
            "SMTP2GO_API_KEY": "api_key",
            "SMTP2GO_SMTP_SERVER": "smtp_server",
            "SMTP2GO_SMTP_PORT": "smtp_port",
            "SMTP2GO_SMTP_USERNAME": "smtp_username",
            "SMTP2GO_SMTP_PASSWORD": "smtp_password",
            "SMTP2GO_SENDER_EMAIL": "sender_email",
            "SMTP2GO_REPORT_RECIPIENTS": "report_recipients",
            "SMTP2GO_REPORT_DIR": "report_dir"
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Handle special cases for conversion
                if config_key == "smtp_port":
                    value = int(value)
                elif config_key == "report_recipients":
                    value = value.split(",")
                
                self.config[config_key] = value
                updated = True
        
        if updated:
            logger.info("Configuration updated from environment variables")
        
        return updated
    
    def update_from_args(self, args):
        """Update configuration from command-line arguments.
        
        Args:
            args (argparse.Namespace): Parsed command-line arguments
            
        Returns:
            bool: True if any configuration was updated, False otherwise
        """
        updated = False
        
        # Convert args to dictionary and filter None values
        args_dict = {k: v for k, v in vars(args).items() if v is not None}
        
        # Remove config_file from the dict as it's not part of our config
        args_dict.pop('config_file', None)
        
        # Update config with args
        for key, value in args_dict.items():
            if key in self.config:
                self.config[key] = value
                updated = True
        
        if updated:
            logger.info("Configuration updated from command-line arguments")
        
        return updated
    
    def validate(self):
        """Validate the configuration for required values.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Required fields
        required = ["api_key", "smtp_username", "smtp_password", "sender_email"]
        missing_fields = []
        
        for field in required:
            if not self.config.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            logger.error(f"Missing required configuration: {', '.join(missing_fields)}")
            logger.error("Please set these values in your environment file or config file")
            logger.error("Environment file location: ~/.smtp2go-usage/env")
            logger.error("Config file location: ~/.smtp2go-usage/config.json")
            return False
        
        # Ensure report_recipients is a list with at least one recipient
        if not isinstance(self.config.get("report_recipients"), list) or not self.config.get("report_recipients"):
            logger.error("No report recipients specified")
            logger.error("Please set SMTP2GO_REPORT_RECIPIENTS in your environment file")
            return False
        
        return True
    
    def get(self, key, default=None):
        """Get a configuration value.
        
        Args:
            key (str): Configuration key
            default: Default value to return if key is not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value.
        
        Args:
            key (str): Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    @staticmethod
    def setup_argparse():
        """Set up command-line argument parsing.
        
        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(description="SMTP2GO Monthly Usage Reporter")
        
        parser.add_argument("-c", "--config-file", 
                          help="Path to configuration file (optional)")
        
        parser.add_argument("--api-key", 
                          help="SMTP2GO API key")
        
        parser.add_argument("--smtp-server", 
                          help="SMTP server for sending reports")
        
        parser.add_argument("--smtp-port", type=int,
                          help="SMTP port for sending reports")
        
        parser.add_argument("--smtp-username", 
                          help="SMTP username for sending reports")
        
        parser.add_argument("--smtp-password", 
                          help="SMTP password for sending reports")
        
        parser.add_argument("--sender-email", 
                          help="Sender email address for reports")
        
        parser.add_argument("--report-recipients", 
                          help="Comma-separated list of email addresses to send reports to")
        
        parser.add_argument("--report-dir", 
                          help="Directory to save generated PDF reports")
        
        
        return parser