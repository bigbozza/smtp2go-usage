"""Tests for the SMTP2GO API client."""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from smtp2go_usage.api_client import SMTP2GoClient

class TestSMTP2GoClient(unittest.TestCase):
    """Test cases for the SMTP2GO API client."""
    
    def setUp(self):
        """Set up test case."""
        self.api_key = "test_api_key"
        self.client = SMTP2GoClient(self.api_key)
    
    def test_init(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.headers["X-Smtp2go-Api-Key"], self.api_key)
        self.assertEqual(self.client.headers["Content-Type"], "application/json")
    
    @patch("smtp2go_usage.api_client.requests.post")
    def test_get_subaccounts(self, mock_post):
        """Test retrieving subaccounts."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "subaccounts": [
                    {"id": "sub1", "name": "Subaccount 1"},
                    {"id": "sub2", "name": "Subaccount 2"},
                ]
            }
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.client.get_subaccounts()
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "sub1")
        self.assertEqual(result[1]["name"], "Subaccount 2")
        
        # Check request
        mock_post.assert_called_once_with(
            f"{self.client.BASE_URL}/subaccounts/search",
            headers=self.client.headers,
            json={}
        )
    
    @patch("smtp2go_usage.api_client.requests.post")
    def test_get_email_history(self, mock_post):
        """Test retrieving email history."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "stats": [
                    {"subaccount_id": "sub1", "sent": 100, "delivered": 95, "failed": 5},
                    {"subaccount_id": "sub2", "sent": 200, "delivered": 190, "failed": 10},
                ]
            }
        }
        mock_post.return_value = mock_response
        
        # Test dates
        start_date = datetime(2025, 2, 1)
        end_date = datetime(2025, 2, 28)
        
        # Call method
        result = self.client.get_email_history(start_date, end_date, ["sub1", "sub2"])
        
        # Assertions
        self.assertEqual(len(result["stats"]), 2)
        self.assertEqual(result["stats"][0]["sent"], 100)
        self.assertEqual(result["stats"][1]["delivered"], 190)
        
        # Check request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"{self.client.BASE_URL}/stats/email_history")
        self.assertEqual(kwargs["headers"], self.client.headers)
        self.assertEqual(kwargs["json"]["subaccounts"], ["sub1", "sub2"])
    
    def test_get_previous_month_range(self):
        """Test calculating the previous month's date range."""
        # Test from a known date (mocking datetime.now())
        with patch("smtp2go_usage.api_client.datetime") as mock_datetime:
            # Mock current date as March 15, 2025
            mock_datetime.now.return_value = datetime(2025, 3, 15)
            
            # Pass through non-mocked methods
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            mock_datetime.timedelta = timedelta
            
            # Call method
            start_date, end_date = SMTP2GoClient.get_previous_month_range()
            
            # Assertions
            self.assertEqual(start_date.year, 2025)
            self.assertEqual(start_date.month, 2)
            self.assertEqual(start_date.day, 1)
            
            self.assertEqual(end_date.year, 2025)
            self.assertEqual(end_date.month, 2)
            self.assertEqual(end_date.day, 28)  # February 2025 has 28 days

if __name__ == "__main__":
    unittest.main()