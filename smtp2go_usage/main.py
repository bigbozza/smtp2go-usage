#!/usr/bin/env python3
"""Main module for the SMTP2GO Monthly Usage Reporter.

This module ties together all components and provides the CLI interface.
"""
import os
import sys
import logging
import datetime
from pathlib import Path

from smtp2go_usage.config import Config
from smtp2go_usage.api_client import SMTP2GoClient
from smtp2go_usage.data_processor import DataProcessor
from smtp2go_usage.pdf_generator import PDFGenerator
from smtp2go_usage.email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser('~/smtp2go-usage.log'))
    ]
)

# Set log level for specific modules to DEBUG
logging.getLogger('smtp2go_usage.api_client').setLevel(logging.DEBUG)
logging.getLogger('smtp2go_usage.data_processor').setLevel(logging.DEBUG)
logging.getLogger('smtp2go_usage.pdf_generator').setLevel(logging.DEBUG)

# Make sure the root logger shows DEBUG messages too
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

def setup_config():
    """Set up and validate configuration.
    
    Returns:
        Config: Validated configuration object or None if validation failed
    """
    # Parse command line arguments
    parser = Config.setup_argparse()
    args = parser.parse_args()
    
    # Initialize configuration
    config = Config()
    
    # Load configuration from environment variables first
    env_updated = config.update_from_env()
    if env_updated:
        logger.info("Configuration loaded from environment variables")
    
    # Try to load from specified file if provided (legacy support)
    if args.config_file:
        logger.warning("Using config file is deprecated. Please use environment variables instead.")
        config.load_from_file(args.config_file)
    elif not env_updated:
        logger.warning("No environment variables found")
        logger.info("Will check command line arguments")
    
    # Update from command line arguments (highest precedence)
    config.update_from_args(args)
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        logger.error("Make sure to set required values either in environment variables, config file, or command line arguments")
        return None
    
    return config

def generate_report(config):
    """Generate the monthly usage report.
    
    Args:
        config (Config): Application configuration
        
    Returns:
        tuple: (success, report_data, pdf_path)
    """
    try:
        # Initialize API client
        api_client = SMTP2GoClient(config.get("api_key"))
        
        # Initialize data processor
        data_processor = DataProcessor(api_client)
        
        # Get report data for the previous month
        start_date, end_date = SMTP2GoClient.get_previous_month_range()
        
        # Always get all subaccounts - ignore specific_subaccounts config
        report_data = data_processor.get_monthly_report_data(
            start_date=start_date,
            end_date=end_date,
            subaccounts=None  # Get all subaccounts
        )
        
        if not report_data:
            logger.error("Failed to get report data")
            return False, None, None
        
        # Initialize PDF generator
        pdf_generator = PDFGenerator(config.get("report_dir"))
        
        # Generate PDF report
        pdf_path = pdf_generator.generate_report(report_data)
        
        if not pdf_path:
            logger.error("Failed to generate PDF report")
            return False, report_data, None
        
        return True, report_data, pdf_path
    
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return False, None, None

def send_report_email(config, report_data, pdf_path):
    """Send the report via email.
    
    Args:
        config (Config): Application configuration
        report_data (dict): Processed report data
        pdf_path (str): Path to the generated PDF report
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Initialize email sender
        email_sender = EmailSender(
            smtp_server=config.get("smtp_server"),
            smtp_port=config.get("smtp_port"),
            username=config.get("smtp_username"),
            password=config.get("smtp_password"),
            sender_email=config.get("sender_email")
        )
        
        # Create email body
        body = email_sender.create_report_email_body(report_data)
        
        # Format email subject
        period = report_data["report_period"]["formatted"]
        subject = config.get("report_subject_template").format(period=period)
        
        # Send email
        recipients = config.get("report_recipients")
        return email_sender.send_report(recipients, subject, body, pdf_path)
    
    except Exception as e:
        logger.error(f"Error sending report email: {e}", exc_info=True)
        return False

def main():
    """Main entry point for the application."""
    logger.info("Starting SMTP2GO Monthly Usage Reporter")
    
    # Setup configuration
    config = setup_config()
    if not config:
        logger.error("Failed to configure application. Exiting.")
        sys.exit(1)
    
    # Generate report
    success, report_data, pdf_path = generate_report(config)
    if not success:
        logger.error("Failed to generate report. Exiting.")
        sys.exit(1)
    
    # Send report email
    if success:
        if send_report_email(config, report_data, pdf_path):
            logger.info(f"Report email sent successfully to {config.get('report_recipients')}")
        else:
            logger.error("Failed to send report email")
            sys.exit(1)
    
    logger.info("SMTP2GO Monthly Usage Reporter completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())