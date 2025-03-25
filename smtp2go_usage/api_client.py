"""SMTP2GO API Client.

This module handles all communication with the SMTP2GO API.
"""
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SMTP2GoClient:
    """Client for interacting with the SMTP2GO API."""
    
    BASE_URL = "https://api.smtp2go.com/v3"
    
    def __init__(self, api_key):
        """Initialize the SMTP2GO API client.
        
        Args:
            api_key (str): SMTP2GO API key for authentication
        """
        self.api_key = api_key
        self.headers = {
            "X-Smtp2go-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
        
    def get_smtp_users(self):
        """Retrieve all SMTP users.
        
        Returns:
            list: List of SMTP user information
        """
        endpoint = f"{self.BASE_URL}/users/smtp/view"
        payload = {}
        
        response = self._make_request(endpoint, payload)
        
        if not response:
            return []
        
        # Check the actual response structure  
        logger.debug(f"Full SMTP users response: {response}")
        
        # The API returns data.results structure based on logs
        if 'data' in response and 'results' in response['data']:
            users = response['data'].get('results', [])
            logger.info(f"Found {len(users)} SMTP users in API response")
            return users
            
        # Fallback to other possible structures if available
        if 'results' in response:
            users = response.get('results', [])
            logger.info(f"Found {len(users)} SMTP users directly in response")
            return users
            
        # Final fallback
        return response.get("data", {}).get("users", [])
    
        
    def get_email_history_by_user(self, start_date, end_date):
        """Get email history for the specified date range, grouped by username.
        
        Args:
            start_date (datetime): Start date for the report
            end_date (datetime): End date for the report
            
        Returns:
            dict: Email history data grouped by username
        """
        endpoint = f"{self.BASE_URL}/stats/email_history"
        
        # Format dates for API
        start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
        end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%S%z")
        
        payload = {
            "group_by": "username",  # API requires "username" not "user"
            "start_date": start_iso,
            "end_date": end_iso
        }
            
        response = self._make_request(endpoint, payload)
        
        if not response:
            return {}
        
        # Log the complete response structure for debugging
        logger.debug(f"Full email history response: {response}")
        
        # Check for nested data structure first
        if 'data' in response and 'history' in response['data']:
            history = response['data'].get('history', [])
            stats = []
            
            # Based on the log output, the structure seems to be different
            for entry in history:
                username = entry.get('username', 'Unknown')
                # Direct values from the history record
                sent = entry.get('used', 0)  # 'used' seems to be the sent count from logs
                bounces = entry.get('bounces', 0)
                rejects = entry.get('rejects', 0)
                
                # Calculate delivered and failed emails
                failed = bounces + rejects
                delivered = sent - failed
                
                logger.debug(f"User {username}: sent={sent}, delivered={delivered}, failed={failed}")
                
                stats.append({
                    'username': username,
                    'sent': sent,
                    'delivered': delivered,
                    'failed': failed
                })
            
            logger.info(f"Processed {len(stats)} user email statistics from API response")
            # Print the results for debugging
            if stats:
                logger.info(f"First user statistics sample: {stats[0]}")
            return {"stats": stats}
        
        # Fallback to direct structure
        if 'history' in response:
            history = response.get('history', [])
            stats = []
            
            # Same processing as above
            for entry in history:
                username = entry.get('username', 'Unknown')
                sent = entry.get('used', 0)
                bounces = entry.get('bounces', 0)
                rejects = entry.get('rejects', 0)
                
                failed = bounces + rejects
                delivered = sent - failed
                
                logger.debug(f"User {username}: sent={sent}, delivered={delivered}, failed={failed}")
                
                stats.append({
                    'username': username,
                    'sent': sent,
                    'delivered': delivered,
                    'failed': failed
                })
            
            logger.info(f"Processed {len(stats)} user email statistics from API response")
            if stats:
                logger.info(f"First user statistics sample: {stats[0]}")
            return {"stats": stats}
        
        # Fallback to the original expected structure
        return response.get("data", {})

    def _make_request(self, endpoint, payload):
        """Make a request to the SMTP2GO API.
        
        Args:
            endpoint (str): API endpoint to call
            payload (dict): Request payload
            
        Returns:
            dict: API response data or None on error
        """
        logger.info(f"Making API request to: {endpoint}")
        logger.info(f"API payload: {payload}")
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload
            )
            logger.info(f"API response status code: {response.status_code}")
            
            response.raise_for_status()
            response_data = response.json()
            
            # Log the response (but keep it secure by not showing too much detail)
            if 'data' in response_data:
                if 'stats' in response_data['data']:
                    logger.info(f"API returned {len(response_data['data']['stats'])} stat records")
                elif 'subaccounts' in response_data['data']:
                    logger.info(f"API returned {len(response_data['data']['subaccounts'])} subaccounts")
                else:
                    logger.info(f"API returned data with keys: {list(response_data['data'].keys())}")
            else:
                logger.info(f"API response keys: {list(response_data.keys())}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if 'response' in locals():
                try:
                    logger.error(f"Response text: {response.text}")
                except:
                    pass
            return None

    @staticmethod
    def get_previous_month_range():
        """Calculate the date range for the previous month.
        
        Returns:
            tuple: (start_date, end_date) as datetime objects
        """
        today = datetime.now()
        
        # Get the first day of the current month
        first_of_current = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get the last day of the previous month (1 day before first of current month)
        last_of_previous = first_of_current - timedelta(days=1)
        
        # Get the first day of the previous month
        first_of_previous = last_of_previous.replace(day=1)
        
        logger.info(f"Using previous month date range: {first_of_previous.strftime('%Y-%m-%d')} to {last_of_previous.strftime('%Y-%m-%d')}")
        
        return first_of_previous, last_of_previous