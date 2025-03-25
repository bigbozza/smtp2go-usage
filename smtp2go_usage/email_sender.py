"""Email Sender for SMTP2GO reports.

This module handles sending the generated PDF reports via email.
"""
import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

logger = logging.getLogger(__name__)

class EmailSender:
    """Send email reports using SMTP."""
    
    def __init__(self, smtp_server, smtp_port, username, password, sender_email):
        """Initialize the email sender.
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
            username (str): SMTP authentication username
            password (str): SMTP authentication password
            sender_email (str): Sender's email address
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email
    
    def send_report(self, recipients, subject, body, pdf_path=None, pdf_bytes=None, pdf_filename=None):
        """Send an email with the PDF report attached.
        
        Args:
            recipients (list): List of email addresses to send the report to
            subject (str): Email subject line
            body (str): Email body content (HTML or plain text)
            pdf_path (str, optional): Path to the PDF file to attach
            pdf_bytes (bytes, optional): PDF content as bytes to attach
            pdf_filename (str, optional): Filename to use when attaching pdf_bytes
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not recipients:
            logger.error("No recipients provided for email")
            return False
        
        # Create multipart message
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'html'))
        
        # Attach PDF
        if pdf_path:
            pdf_filename = os.path.basename(pdf_path)
            try:
                with open(pdf_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                    msg.attach(attachment)
            except Exception as e:
                logger.error(f"Failed to attach PDF file {pdf_path}: {e}")
                return False
        elif pdf_bytes and pdf_filename:
            attachment = MIMEApplication(pdf_bytes, _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            msg.attach(attachment)
        
        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def create_report_email_body(self, report_data):
        """Create a formatted HTML email body for the report.
        
        Args:
            report_data (dict): Report data to include in the email
            
        Returns:
            str: Formatted HTML email body
        """
        period = report_data['report_period']['formatted']
        summary = report_data['summary']
        users = report_data['users']
        
        # Create HTML email body
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                h1 {{ color: #2c5aa0; }}
                h2 {{ color: #2c5aa0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #4472C4; color: white; }}
                .summary {{ margin-bottom: 20px; }}
                .footer {{ font-size: small; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <h1>SMTP2GO Monthly Usage Report</h1>
            <p>Please find attached the SMTP2GO usage report for <strong>{period}</strong>.</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <ul>
                    <li>Total Emails Sent: <strong>{summary['total_sent']:,}</strong></li>
                    <li>Total Emails Delivered: <strong>{summary['total_delivered']:,}</strong></li>
                    <li>Total Emails Failed: <strong>{summary['total_failed']:,}</strong></li>
                    <li>Overall Delivery Rate: <strong>{summary['delivery_rate']:.2f}%</strong></li>
                    <li>Total Users: <strong>{summary['total_users']}</strong></li>
                </ul>
            </div>
        """
        
        # Add top 5 users table
        top_users = users[:5] if len(users) > 5 else users
        
        if top_users:
            html += """
            <h2>Top Users by Volume</h2>
            <table>
                <tr>
                    <th>Username</th>
                    <th>Emails Sent</th>
                    <th>Delivery Rate</th>
                </tr>
            """
            
            for user in top_users:
                username = user.get('username', "Unknown")
                html += f"""
                <tr>
                    <td>{username}</td>
                    <td>{user['sent']:,}</td>
                    <td>{user['delivery_rate']:.2f}%</td>
                </tr>
                """
            
            html += "</table>"
        
        # Add footer
        html += """
            <div class="footer">
                <p>This report was automatically generated by the SMTP2GO Monthly Usage Reporter. 
                For detailed information, please see the attached PDF report.</p>
            </div>
        </body>
        </html>
        """
        
        return html