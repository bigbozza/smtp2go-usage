# SMTP2GO Monthly Usage Reporter

## Project Overview
Create a Python application that:
1. Automatically generates PDF reports of SMTP2GO usage statistics for all subaccounts
2. Emails these reports to specified recipients
3. Runs automatically at the beginning of each month
4. Shows usage data from the previous month

## Technical Requirements
- Python 3.8+
- Access to SMTP2GO API credentials
- Ability to send emails programmatically
- PDF generation capabilities
- Automated scheduling

## API Documentation

### Authentication
- All requests require an API key
- Use the X-Smtp2go-Api-Key header for authentication
- Base URL: https://api.smtp2go.com/v3

### Key Endpoint: Email History
- **URL**: https://api.smtp2go.com/v3/stats/email_history
- **Method**: POST
- **Parameters**:
  - `group_by`: Set to "subaccount" to group results by subaccount
  - `start_date`: ISO-8601 formatted datetime for start of reporting period
  - `end_date`: ISO-8601 formatted datetime for end of reporting period
  - `subaccounts`: Optional array of specific subaccount IDs to report on

### Getting Subaccount Information
- Use the `/subaccounts/search` endpoint to retrieve subaccount IDs

## Implementation Details

### Core Components
1. **API Client**: Create a module to handle SMTP2GO API requests and authentication
2. **Data Processor**: Handle and organize the usage data from the API
3. **PDF Generator**: Convert processed data into PDF reports
4. **Email Sender**: Send the generated reports via email
5. **Scheduler**: Run the report generation at the start of each month

### Application Flow
1. Determine the date range for the previous month
2. Retrieve all subaccount IDs (or use specific ones if provided)
3. Fetch usage statistics for each subaccount for the previous month
4. Generate a comprehensive PDF report with usage data
5. Email the report to specified recipients
6. Log the successful completion or any errors

## Required Features
1. **Configuration Management**:
   - Store API keys, email recipients, and other settings securely
   - Support for command-line arguments to override default settings

2. **Robust Error Handling**:
   - Graceful handling of API errors
   - Retry logic for transient failures
   - Comprehensive logging

3. **PDF Report Contents**:
   - Summary of total emails sent across all subaccounts
   - Per-subaccount usage statistics
   - Visual graphs/charts for easy data interpretation
   - Comparison with previous periods

4. **Email Delivery**:
   - Professional formatting of the email body
   - PDF attachments
   - Subject line indicating the reporting period

5. **Scheduling**:
   - Cron job or similar mechanism to trigger reports on the 1st of each month
   - Option for manual triggering

## Output Examples
- PDF report showing email volume, delivery rates, and other metrics by subaccount
- Email with summary in the body and the detailed PDF report attached

## Future Enhancements (Optional)
- Web dashboard for viewing historical reports
- Additional report formats (CSV, Excel)
- Custom reporting periods
