# SMTP2GO Monthly Usage Reporter

A Python application that automatically generates and emails PDF reports of SMTP2GO usage statistics for all subaccounts.

## Features

- Automatically retrieves usage statistics from the SMTP2GO API
- Generates professional PDF reports with visualizations
- Emails reports to specified recipients
- Designed to run automatically at the beginning of each month
- Customizable configuration via file, environment variables, or command-line arguments

## Installation

### Prerequisites

- Python 3.8 or higher
- SMTP2GO API key
- SMTP credentials for sending emails

### Installing from source

1. Clone this repository:
   ```
   git clone https://github.com/user/smtp2go-usage.git
   cd smtp2go-usage
   ```

2. Install the package:
   ```
   pip install -e .
   ```

### Running Without Installation

You can also run the application directly without installation. First, activate the virtual environment:

```bash
source bin/activate
```

Then run the application:

```bash
python smtp2go_usage/main.py
```

Alternatively, use the provided helper script which handles virtual environment activation automatically:

```bash
./scripts/run_monthly_report.sh
```

## Configuration

Configuration can be provided in two ways (in order of precedence):

1. Command-line arguments
2. Environment variables (recommended)

### Environment Variables (Recommended)

The simplest way to configure the application is through environment variables:

1. Copy the sample environment file:
```bash
mkdir -p ~/.smtp2go-usage
cp env.sample ~/.smtp2go-usage/env
```

2. Edit the file to add your API key, SMTP credentials, and recipient email addresses:
```bash
nano ~/.smtp2go-usage/env
```

The following environment variables are supported:

- `SMTP2GO_API_KEY`: Your SMTP2GO API key (required)
- `SMTP2GO_SMTP_SERVER`: SMTP server address (default: smtp2go.com)
- `SMTP2GO_SMTP_PORT`: SMTP server port (default: 587)
- `SMTP2GO_SMTP_USERNAME`: SMTP username (required)
- `SMTP2GO_SMTP_PASSWORD`: SMTP password (required)
- `SMTP2GO_SENDER_EMAIL`: Sender email address (required)
- `SMTP2GO_REPORT_RECIPIENTS`: Comma-separated list of recipient email addresses (required)
- `SMTP2GO_REPORT_DIR`: Directory to save generated PDF reports (optional)


### Command-line Arguments

Run with `--help` to see available command-line options:

```bash
smtp2go-usage --help
```

## Usage

### Manual Execution

Run the reporter manually:

```bash
smtp2go-usage
```

### Automated Execution with Cron

To run the reporter automatically at the beginning of each month, add a cron job:

```bash
crontab -e
```

Add one of the following lines to run at 1:00 AM on the 1st of each month:

If you installed the package:
```
0 1 1 * * smtp2go-usage
```

If you're running from source (the script handles venv activation):
```
0 1 1 * * /home/boz/Applications/smtp2go-usage/scripts/run_monthly_report.sh
```

## Generated Reports

Reports are generated as PDF files in the configured report directory (default: `~/smtp2go-reports`).

Each report contains:
- Summary statistics for the previous month
- Detailed usage by subaccount
- Visualizations of email volume and delivery rates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please contact support@example.com.