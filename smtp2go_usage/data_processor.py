"""Data Processor for SMTP2GO usage data.

This module processes and organizes usage data from the SMTP2GO API.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and organize SMTP2GO usage data."""
    
    def __init__(self, api_client):
        """Initialize the data processor.
        
        Args:
            api_client (SMTP2GoClient): Instance of the SMTP2GO API client
        """
        self.api_client = api_client
        
    def get_monthly_report_data(self, start_date=None, end_date=None, *args, **kwargs):
        """Get processed monthly report data based on SMTP users.
        
        Args:
            start_date (datetime, optional): Start date for report period
            end_date (datetime, optional): End date for report period
            
        Returns:
            dict: Processed report data with usage statistics
        """
        # If dates not provided, use previous month
        if not start_date or not end_date:
            start_date, end_date = self.api_client.get_previous_month_range()
            logger.info(f"Using date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
        # Get all SMTP users
        logger.info("Retrieving all SMTP users from API")
        user_list = self.api_client.get_smtp_users()
        
        if not user_list:
            logger.warning("No SMTP users returned from API")
        else:
            logger.info(f"Retrieved {len(user_list)} SMTP users")
            # Log user details for debugging
            for user in user_list:
                logger.debug(f"SMTP User: {user.get('username', 'Unnamed')}")
            
        # Get email history data by user
        logger.info(f"Retrieving email history grouped by username")
        email_history = self.api_client.get_email_history_by_user(
            start_date, 
            end_date
        )
        
        if not email_history:
            logger.warning("No email history data returned from API")
            
        # Process the data
        result = self._process_user_report_data(
            email_history, 
            user_list, 
            start_date, 
            end_date
        )
        
        logger.info(f"Generated report data with {len(result.get('users', []))} users")
        
        if len(result.get('users', [])) == 0:
            logger.warning("No data found for the specified time period and users")
            logger.warning("This could be because there were no emails sent during this period,")
            logger.warning("or because the API key doesn't have access to the requested data.")
            
        return result
    
    
    def _process_user_report_data(self, email_history, user_list, start_date, end_date):
        """Process raw API data into a structured report format for SMTP users.
        
        Args:
            email_history (dict): Raw email history data from API, grouped by username
            user_list (list): List of SMTP user information
            start_date (datetime): Start date of the report period
            end_date (datetime): End date of the report period
            
        Returns:
            dict: Processed report data
        """
        # Create mapping of usernames to user info
        username_map = {user.get('username'): user for user in user_list}
        
        # Extract statistics by user
        user_stats = email_history.get('stats', [])
        logger.debug(f"Processing user stats: {user_stats}")
        
        # Calculate total emails sent
        total_sent = sum(stat.get('sent', 0) for stat in user_stats)
        total_delivered = sum(stat.get('delivered', 0) for stat in user_stats)
        total_failed = sum(stat.get('failed', 0) for stat in user_stats)
        
        logger.info(f"Total stats: sent={total_sent}, delivered={total_delivered}, failed={total_failed}")
        
        # Calculate delivery rate
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        
        # Format user stats
        formatted_stats = []
        for stat in user_stats:
            # The API returns 'username' not 'user' when using group_by=username
            username = stat.get('username')
            
            # Get user info if available
            user_info = username_map.get(username, {})
            
            sent = stat.get('sent', 0)
            delivered = stat.get('delivered', 0)
            failed = stat.get('failed', 0)
            
            # Calculate delivery rate for this user
            user_delivery_rate = (delivered / sent * 100) if sent > 0 else 0
            
            formatted_stats.append({
                'username': username,
                'name': user_info.get('name', username),  # Use name if available, otherwise username
                'email': user_info.get('email', ''),
                'sent': sent,
                'delivered': delivered,
                'failed': failed,
                'delivery_rate': user_delivery_rate
            })
        
        # Sort by number of emails sent (descending)
        formatted_stats.sort(key=lambda x: x['sent'], reverse=True)
        
        # Create report data structure
        report_data = {
            'report_period': {
                'start_date': start_date,
                'end_date': end_date,
                'formatted': f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
            },
            'summary': {
                'total_sent': total_sent,
                'total_delivered': total_delivered,
                'total_failed': total_failed,
                'delivery_rate': delivery_rate,
                'total_users': len(formatted_stats)
            },
            'users': formatted_stats,
            'generated_at': datetime.now()
        }
        
        return report_data