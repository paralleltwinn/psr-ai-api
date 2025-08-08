# =============================================================================
# POORNASREE AI - EMAIL SERVICE
# =============================================================================

"""
Email service for sending notifications, verification emails, and HTML templates.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..config import settings
from ..database.models import User, Notification
from ..core.constants import UserRole, NotificationType

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with HTML templates."""
    
    def __init__(self):
        self.smtp_server = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.mail_from
        self.use_tls = settings.smtp_use_tls
    
    def _get_smtp_connection(self):
        """Create SMTP connection."""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"SMTP connection error: {e}")
            raise
    
    def _create_html_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> MIMEMultipart:
        """Create HTML email message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        
        # Add text version if provided
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        return msg
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email with HTML content."""
        try:
            msg = self._create_html_email(to_email, subject, html_content, text_content)
            
            with self._get_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_bulk_email(
        self, 
        recipients: List[str], 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, bool]:
        """Send email to multiple recipients."""
        results = {}
        
        try:
            with self._get_smtp_connection() as server:
                for email in recipients:
                    try:
                        msg = self._create_html_email(email, subject, html_content, text_content)
                        server.send_message(msg)
                        results[email] = True
                        logger.info(f"Email sent successfully to {email}")
                    except Exception as e:
                        results[email] = False
                        logger.error(f"Failed to send email to {email}: {e}")
        
        except Exception as e:
            logger.error(f"SMTP connection failed for bulk email: {e}")
            for email in recipients:
                results[email] = False
        
        return results


# Initialize email service
email_service = EmailService()


def get_base_email_template(title: str, content: str, primary_color: str = "#6366f1") -> str:
    """Base modern email template with consistent design."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>{title} - Poornasree AI</title>
        <!--[if mso]>
        <noscript>
            <xml>
                <o:OfficeDocumentSettings>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
            </xml>
        </noscript>
        <![endif]-->
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #374151;
                background-color: #f9fafb;
                margin: 0;
                padding: 0;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }}
            
            .email-header {{
                background: linear-gradient(135deg, {primary_color} 0%, #4f46e5 100%);
                padding: 40px 30px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            
            .logo {{
                width: 48px;
                height: 48px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                margin-bottom: 16px;
            }}
            
            .email-title {{
                color: #ffffff;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            }}
            
            .email-subtitle {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin: 8px 0 0 0;
                font-weight: 400;
            }}
            
            .email-content {{
                padding: 40px 30px;
                background-color: #ffffff;
            }}
            
            .greeting {{
                font-size: 20px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 16px;
            }}
            
            .content-text {{
                font-size: 16px;
                color: #374151;
                margin-bottom: 24px;
                line-height: 1.7;
            }}
            
            .highlight-box {{
                background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                border-left: 4px solid {primary_color};
                padding: 20px;
                margin: 24px 0;
                border-radius: 0 8px 8px 0;
            }}
            
            .cta-button {{
                display: inline-block;
                background: linear-gradient(135deg, {primary_color} 0%, #4f46e5 100%);
                color: #ffffff;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 16px;
                margin: 16px 0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }}
            
            .cta-button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
            }}
            
            .secondary-button {{
                display: inline-block;
                background: #f9fafb;
                color: {primary_color};
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                border: 2px solid #e5e7eb;
                margin: 8px 4px;
            }}
            
            .info-list {{
                background-color: #f9fafb;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            
            .info-list ul {{
                margin: 0;
                padding-left: 20px;
            }}
            
            .info-list li {{
                margin-bottom: 8px;
                color: #374151;
            }}
            
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent 0%, #e5e7eb 50%, transparent 100%);
                margin: 32px 0;
            }}
            
            .email-footer {{
                background-color: #f9fafb;
                padding: 30px;
                text-align: center;
                border-radius: 0 0 8px 8px;
                border-top: 1px solid #e5e7eb;
            }}
            
            .footer-text {{
                font-size: 14px;
                color: #6b7280;
                margin: 4px 0;
            }}
            
            .footer-link {{
                color: {primary_color};
                text-decoration: none;
            }}
            
            .text-center {{
                text-align: center;
            }}
            
            .text-muted {{
                color: #6b7280;
                font-size: 14px;
            }}
            
            @media only screen and (max-width: 600px) {{
                .email-container {{
                    margin: 0 !important;
                    border-radius: 0 !important;
                }}
                
                .email-header,
                .email-content,
                .email-footer {{
                    padding: 20px !important;
                }}
                
                .email-title {{
                    font-size: 24px !important;
                }}
                
                .cta-button {{
                    display: block !important;
                    text-align: center !important;
                    margin: 20px 0 !important;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <div class="logo">🚀</div>
                <h1 class="email-title">{title}</h1>
                <p class="email-subtitle">Poornasree AI</p>
            </div>
            
            <div class="email-content">
                {content}
            </div>
            
            <div class="email-footer">
                <p class="footer-text">© 2025 Poornasree AI. All rights reserved.</p>
                <p class="footer-text">This is an automated message, please do not reply to this email.</p>
                <div class="divider"></div>
                <p class="footer-text">
                    Questions? Contact our <a href="mailto:support@poornasreeai.com" class="footer-link">support team</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def get_verification_email_template(user_name: str, verification_link: str) -> str:
    """Get HTML template for email verification."""
    content = f"""
        <div class="greeting">Hello {user_name}!</div>
        <p class="content-text">
            Welcome to Poornasree AI! We're excited to have you join our platform. 
            To complete your registration and secure your account, please verify your email address.
        </p>
        
        <div class="text-center">
            <a href="{verification_link}" class="cta-button">Verify Email Address</a>
        </div>
        
        <div class="highlight-box">
            <p><strong>🔒 Security Notice:</strong> This verification link will expire in 24 hours for your security.</p>
        </div>
        
        <p class="content-text">
            If the button above doesn't work, you can copy and paste this link into your browser:
        </p>
        <div style="background: #f3f4f6; padding: 12px; border-radius: 6px; word-break: break-all; font-family: monospace; font-size: 14px; margin: 16px 0;">
            {verification_link}
        </div>
        
        <p class="text-muted">
            If you didn't create an account with us, you can safely ignore this email.
        </p>
    """
    return get_base_email_template("Email Verification", content, "#10b981")


def get_otp_email_template(user_name: str, otp_code: str) -> str:
    """Get HTML template for OTP verification."""
    content = f"""
        <div class="greeting">Hello {user_name}!</div>
        <p class="content-text">
            You requested a one-time password (OTP) for secure access to your account. 
            Please use the verification code below:
        </p>
        
        <div class="text-center">
            <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; font-size: 32px; font-weight: bold; padding: 24px; border-radius: 12px; letter-spacing: 8px; margin: 24px 0; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                {otp_code}
            </div>
        </div>
        
        <div class="info-list">
            <p><strong>🛡️ Important Security Information:</strong></p>
            <ul>
                <li>This OTP is valid for <strong>10 minutes</strong> only</li>
                <li>Never share this code with anyone</li>
                <li>Our team will never ask for this code</li>
                <li>If you didn't request this, please contact support immediately</li>
            </ul>
        </div>
        
        <p class="text-muted">
            If you didn't request this verification code, please ignore this email and ensure your account is secure.
        </p>
    """
    return get_base_email_template("Security Code", content)


def get_registration_otp_template(user_name: str, otp_code: str) -> str:
    """Get HTML template for registration OTP verification."""
    content = f"""
        <div class="greeting">Welcome {user_name}!</div>
        <p class="content-text">
            Thank you for choosing Poornasree AI! To complete your account registration, 
            please verify your email address using the secure code below:
        </p>
        
        <div class="text-center">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; font-size: 32px; font-weight: bold; padding: 24px; border-radius: 12px; letter-spacing: 8px; margin: 24px 0; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                {otp_code}
            </div>
        </div>
        
        <div class="highlight-box">
            <p><strong>📝 Registration Process:</strong></p>
            <p>Enter this code in the verification form to activate your account and start using our AI services.</p>
        </div>
        
        <div class="info-list">
            <p><strong>⏰ Time-sensitive Information:</strong></p>
            <ul>
                <li>This verification code expires in <strong>10 minutes</strong></li>
                <li>You can request a new code if this one expires</li>
                <li>Keep this code secure and don't share it with anyone</li>
            </ul>
        </div>
        
        <p class="text-muted">
            If you didn't attempt to create an account, you can safely ignore this email.
        </p>
    """
    return get_base_email_template("Registration Verification", content, "#10b981")


def get_welcome_email_template(user_name: str, user_role: str) -> str:
    """Get HTML template for welcome email."""
    role_features = {
        "customer": [
            "Submit support tickets and track their progress",
            "Access AI-powered solutions for your machine models",
            "Get personalized recommendations based on your state location",
            "Receive priority customer support"
        ],
        "engineer": [
            "Access advanced engineering tools and dashboards",
            "Collaborate with other engineers on projects",
            "Manage customer support tickets and solutions",
            "Access detailed analytics and reporting features"
        ],
        "admin": [
            "Manage user accounts and permissions",
            "Review and approve engineer applications",
            "Access comprehensive system analytics",
            "Configure system settings and policies"
        ]
    }
    
    features = role_features.get(user_role.lower(), role_features["customer"])
    features_html = "".join([f"<li>{feature}</li>" for feature in features])
    
    content = f"""
        <div class="greeting">Welcome to Poornasree AI, {user_name}!</div>
        <p class="content-text">
            🎉 Congratulations! Your account has been successfully created and activated. 
            We're thrilled to have you join our innovative AI platform as a <strong>{user_role.title()}</strong>.
        </p>
        
        <div class="highlight-box">
            <p><strong>🚀 What's Next?</strong></p>
            <p>Your account is now ready to use. You can log in and start exploring all the features available to you.</p>
        </div>
        
        <div class="text-center">
            <a href="http://localhost:3000/login" class="cta-button">Start Using Poornasree AI</a>
        </div>
        
        <div class="info-list">
            <p><strong>✨ Your {user_role.title()} Features Include:</strong></p>
            <ul>
                {features_html}
            </ul>
        </div>
        
        <div class="divider"></div>
        
        <p class="content-text">
            <strong>🛟 Need Help Getting Started?</strong><br>
            Our support team is here to help you make the most of your Poornasree AI experience. 
            Don't hesitate to reach out if you have any questions.
        </p>
        
        <div class="text-center">
            <a href="mailto:support@poornasreeai.com" class="secondary-button">Contact Support</a>
            <a href="#" class="secondary-button">View Documentation</a>
        </div>
    """
    return get_base_email_template("Welcome to Poornasree AI", content, "#10b981")


def get_engineer_application_template(user_name: str, department: str, admin_name: str) -> str:
    """Get HTML template for engineer application submission."""
    content = f"""
        <div class="greeting">Hello {user_name}!</div>
        <p class="content-text">
            Thank you for your interest in joining Poornasree AI as an engineer in the <strong>{department}</strong> department. 
            Your application has been successfully submitted and is now under review.
        </p>
        
        <div class="highlight-box">
            <p><strong>📋 Application Status: Pending Review</strong></p>
            <p>Your application is currently being reviewed by our admin team. We'll notify you once a decision has been made.</p>
        </div>
        
        <div class="info-list">
            <p><strong>📝 What Happens Next:</strong></p>
            <ul>
                <li><strong>Review Process:</strong> Our team will carefully evaluate your application</li>
                <li><strong>Verification:</strong> We may contact you for additional information</li>
                <li><strong>Decision:</strong> You'll receive an email with the final decision</li>
                <li><strong>Timeline:</strong> Most applications are reviewed within 2-3 business days</li>
            </ul>
        </div>
        
        <div class="info-list">
            <p><strong>📞 Application Details:</strong></p>
            <ul>
                <li><strong>Department:</strong> {department}</li>
                <li><strong>Reviewing Admin:</strong> {admin_name}</li>
                <li><strong>Submission Date:</strong> {datetime.now().strftime('%B %d, %Y')}</li>
                <li><strong>Application ID:</strong> ENG-{datetime.now().strftime('%Y%m%d')}-{user_name[:3].upper()}</li>
            </ul>
        </div>
        
        <div class="divider"></div>
        
        <p class="content-text">
            <strong>💡 While You Wait:</strong><br>
            Feel free to explore our platform documentation and familiarize yourself with our engineering processes and tools.
        </p>
        
        <div class="text-center">
            <a href="#" class="secondary-button">View Documentation</a>
            <a href="mailto:support@poornasreeai.com" class="secondary-button">Contact Support</a>
        </div>
        
        <p class="text-muted">
            Questions about your application? Reply to this email or contact our support team.
        </p>
    """
    return get_base_email_template("Engineer Application Received", content, "#f59e0b")


def get_admin_engineer_application_template(engineer_name: str, engineer_email: str, application_id: int, approve_token: str = None, reject_token: str = None) -> str:
    """Get HTML template for admin engineer application notification with direct action buttons."""
    from ..config import settings
    
    # Base URLs for actions
    api_base_url = settings.api_base_url or "http://localhost:8000"
    dashboard_url = f"{settings.frontend_url or 'http://localhost:3000'}/dashboard"
    
    # Create direct action URLs if tokens are provided
    if approve_token and reject_token:
        approve_url = f"{api_base_url}/api/v1/admin/email-action/approve/{approve_token}"
        reject_url = f"{api_base_url}/api/v1/admin/email-action/reject/{reject_token}"
        action_buttons = f"""
            <div class="text-center">
                <a href="{approve_url}" class="cta-button" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); margin: 8px;">✅ APPROVE APPLICATION</a>
                <a href="{reject_url}" class="cta-button" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); margin: 8px;">❌ REJECT APPLICATION</a>
            </div>
            
            <div class="highlight-box" style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-left-color: #10b981;">
                <p><strong>🚀 One-Click Actions:</strong> Click the buttons above to instantly approve or reject this application. No login required!</p>
                <p><small>⚠️ These action links expire in 7 days and are unique to your email address.</small></p>
            </div>
        """
    else:
        action_buttons = f"""
            <div class="text-center">
                <a href="{dashboard_url}" class="cta-button">Go to Admin Dashboard</a>
            </div>
        """
    
    content = f"""
        <div class="greeting">Admin Action Required!</div>
        <p class="content-text">
            ⏰ A new engineer application has been submitted and requires your immediate review and approval.
        </p>
        
        <div class="highlight-box" style="background: linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%); border-left-color: #f59e0b;">
            <p><strong>📋 New Engineer Application</strong></p>
            <p>Status: <span style="color: #f59e0b; font-weight: bold;">PENDING REVIEW</span></p>
        </div>
        
        <div class="info-list">
            <p><strong>👤 Applicant Details:</strong></p>
            <ul>
                <li><strong>Name:</strong> {engineer_name}</li>
                <li><strong>Email:</strong> {engineer_email}</li>
                <li><strong>Application ID:</strong> #{application_id}</li>
                <li><strong>Applied At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
            </ul>
        </div>
        
        <div class="divider"></div>
        
        <h3 style="color: #111827; margin: 24px 0 16px 0;">🚀 Quick Actions:</h3>
        {action_buttons}
        
        <div class="info-list">
            <p><strong>📋 Review Guidelines:</strong></p>
            <ul>
                <li>✓ Verify applicant's email and contact information</li>
                <li>✓ Review submitted department and experience</li>
                <li>✓ Check application completeness</li>
                <li>✓ Evaluate fit for engineering role</li>
                <li>✓ Make approval/rejection decision</li>
            </ul>
        </div>
        
        <div class="text-center">
            <a href="{dashboard_url}" class="secondary-button">🏠 Go to Admin Dashboard</a>
        </div>
        
        <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 24px 0; border-left: 3px solid #6366f1;">
            <p style="margin: 0; font-size: 14px; color: #374151;"><strong>🔒 Security Notice:</strong> Action links are personalized and secure. They expire automatically and can only be used once.</p>
        </div>
    """
    return get_base_email_template("🚨 NEW Engineer Application - Take Action Now", content, "#f59e0b")
    """Get HTML template for engineer application notification with direct action buttons."""
    
    # Base URLs for actions
    api_base_url = settings.api_base_url or "http://localhost:8000"
    dashboard_url = f"{settings.frontend_url or 'http://localhost:3000'}/dashboard"
    
    # Create direct action URLs if tokens are provided
    if approve_token and reject_token:
        approve_url = f"{api_base_url}/api/v1/admin/email-action/approve/{approve_token}"
        reject_url = f"{api_base_url}/api/v1/admin/email-action/reject/{reject_token}"
        action_buttons = f"""
            <div class="action-buttons">
                <a href="{approve_url}" class="approve-btn">✅ APPROVE APPLICATION</a>
                <a href="{reject_url}" class="reject-btn">❌ REJECT APPLICATION</a>
            </div>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #28a745;">
                <p><strong>🚀 One-Click Actions:</strong> Click the buttons above to instantly approve or reject this application. No login required!</p>
                <p><small>⚠️ These action links expire in 7 days and are unique to your email address.</small></p>
            </div>
        """
    else:
        action_buttons = f"""
            <div class="action-buttons">
                <a href="{dashboard_url}" class="approve-btn">Go to Dashboard</a>
            </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Engineer Application - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .applicant-info {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
            .action-buttons {{ text-align: center; margin: 30px 0; }}
            .approve-btn {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold; transition: background 0.3s; }}
            .approve-btn:hover {{ background: #1e7e34; }}
            .reject-btn {{ display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold; transition: background 0.3s; }}
            .reject-btn:hover {{ background: #bd2130; }}
            .dashboard-btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
            .urgent {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .security-note {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 12px; color: #666; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📋 Poornasree AI</div>
            <h1>New Engineer Application</h1>
        </div>
        <div class="content">
            <div class="urgent">
                <strong>⏰ Action Required:</strong> A new engineer application is pending your review and approval.
            </div>
            
            <h2>Engineer Role Application</h2>
            <p>A new user has applied for Engineer role and requires immediate attention.</p>
            
            <div class="applicant-info">
                <h3>📋 Applicant Details:</h3>
                <p><strong>Name:</strong> {engineer_name}</p>
                <p><strong>Email:</strong> {engineer_email}</p>
                <p><strong>Application ID:</strong> #{application_id}</p>
                <p><strong>Applied At:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p><strong>Status:</strong> <span style="color: #ffc107; font-weight: bold;">PENDING REVIEW</span></p>
            </div>
            
            <h3>🚀 Quick Actions:</h3>
            {action_buttons}
            
            <h3>� Review Guidelines:</h3>
            <ul style="background: white; padding: 20px; border-radius: 5px;">
                <li>✓ Verify applicant's email and contact information</li>
                <li>✓ Review submitted department and experience</li>
                <li>✓ Check application completeness</li>
                <li>✓ Evaluate fit for engineering role</li>
                <li>✓ Make approval/rejection decision</li>
            </ul>
            
            <div class="action-buttons">
                <a href="{dashboard_url}" class="dashboard-btn">🏠 Go to Admin Dashboard</a>
            </div>
            
            <div class="security-note">
                <p><strong>🔒 Security Notice:</strong> Action links are personalized and secure. They expire automatically and can only be used once.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>This email was sent to you because you are an administrator for Poornasree AI.</p>
            <p>If you believe this email was sent in error, please contact the system administrator.</p>
            <p style="color: #999; font-size: 12px;">
                © {datetime.now().year} Poornasree AI. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """


def get_engineer_approval_template(engineer_name: str) -> str:
    """Get HTML template for engineer approval notification."""
    content = f"""
        <div class="greeting">Congratulations {engineer_name}!</div>
        <p class="content-text">
            🎉 Excellent news! Your engineer application has been reviewed and <strong>approved</strong> by our admin team. 
            Welcome to the Poornasree AI engineering team!
        </p>
        
        <div class="highlight-box" style="background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); border-left-color: #10b981;">
            <p><strong>✅ Application Status: APPROVED</strong></p>
            <p>Your account has been upgraded with full engineer privileges and access to all engineering tools.</p>
        </div>
        
        <div class="text-center">
            <a href="http://localhost:3000/login" class="cta-button">Access Your Engineer Dashboard</a>
        </div>
        
        <div class="info-list">
            <p><strong>🚀 Your New Engineer Features:</strong></p>
            <ul>
                <li>Access to advanced engineering tools and dashboards</li>
                <li>Collaborate with other engineers on projects</li>
                <li>Manage customer support tickets and solutions</li>
                <li>Access detailed analytics and reporting features</li>
                <li>Participate in engineering team discussions</li>
            </ul>
        </div>
        
        <div class="divider"></div>
        
        <p class="content-text">
            <strong>🎯 Getting Started:</strong><br>
            Log in to your account to explore your new engineer dashboard and start collaborating with the team. 
            Your engineering journey with Poornasree AI begins now!
        </p>
        
        <div class="text-center">
            <a href="#" class="secondary-button">View Engineer Guide</a>
            <a href="mailto:engineering@poornasreeai.com" class="secondary-button">Contact Engineering Team</a>
        </div>
    """
    return get_base_email_template("Application Approved - Welcome to the Team!", content, "#10b981")


def get_engineer_rejection_template(engineer_name: str, reason: str = "") -> str:
    """Get HTML template for engineer rejection notification."""
    content = f"""
        <div class="greeting">Hello {engineer_name},</div>
        <p class="content-text">
            Thank you for your interest in joining Poornasree AI as an engineer. 
            After careful review of your application, we have decided not to move forward at this time.
        </p>
        
        <div class="highlight-box" style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-left-color: #ef4444;">
            <p><strong>📋 Application Status: Not Approved</strong></p>
            <p>While we cannot offer you a position at this time, we appreciate your interest in our platform.</p>
        </div>
        
        {f'''
        <div class="info-list">
            <p><strong>💬 Feedback from Review:</strong></p>
            <p style="font-style: italic; color: #6b7280; padding: 16px; background: #f9fafb; border-radius: 6px; border-left: 3px solid #ef4444;">
                "{reason}"
            </p>
        </div>
        ''' if reason else ''}
        
        <div class="info-list">
            <p><strong>� Moving Forward:</strong></p>
            <ul>
                <li>Continue developing your technical skills and experience</li>
                <li>Stay engaged with our platform as a customer</li>
                <li>Consider reapplying in the future as you gain more experience</li>
                <li>Connect with our community and learning resources</li>
            </ul>
        </div>
        
        <div class="divider"></div>
        
        <p class="content-text">
            <strong>🌟 Future Opportunities:</strong><br>
            We encourage you to continue your professional development and consider reapplying when you have 
            additional experience. We appreciate your interest in Poornasree AI.
        </p>
        
        <div class="text-center">
            <a href="http://localhost:3000/dashboard" class="secondary-button">Continue as Customer</a>
            <a href="mailto:careers@poornasreeai.com" class="secondary-button">Career Questions</a>
        </div>
        
        <p class="text-muted">
            Thank you for considering Poornasree AI as part of your career journey.
        </p>
    """
    return get_base_email_template("Application Status Update", content, "#ef4444")


# Email sending functions
async def send_verification_email(user: User, verification_link: str) -> bool:
    """Send email verification email."""
    try:
        subject = "Verify Your Email - Poornasree AI"
        html_content = get_verification_email_template(user.first_name, verification_link)
        
        return email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        return False


async def send_otp_email(user: User, otp_code: str, purpose: str = "login") -> bool:
    """Send OTP verification email."""
    try:
        if purpose == "registration":
            subject = "Complete Your Registration - Poornasree AI"
            html_content = get_registration_otp_template(user.first_name or "User", otp_code)
        else:
            subject = "Your Login Code - Poornasree AI"
            html_content = get_otp_email_template(user.first_name or "User", otp_code)
        
        return email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send OTP email to {user.email}: {e}")
        return False


async def send_welcome_email(user: User) -> bool:
    """Send welcome email after verification."""
    try:
        subject = "Welcome to Poornasree AI!"
        html_content = get_welcome_email_template(user.first_name, user.role.value)
        
        return email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False


async def send_password_reset_email(user: User, reset_link: str) -> bool:
    """Send password reset email."""
    try:
        subject = "Password Reset Request - Poornasree AI"
        html_content = f"""
        <h2>Password Reset Request</h2>
        <p>Hello {user.first_name},</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        return email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False


async def send_engineer_application_notification(engineer: User, admin_emails: List[str], application_id: int) -> bool:
    """Send engineer application notification to admins with direct action buttons."""
    try:
        from ..auth.auth import create_action_token
        from datetime import timedelta
        
        subject = "🚨 NEW Engineer Application - Take Action Now"
        
        # Send personalized emails to each admin with their own action tokens
        results = []
        for admin_email in admin_emails:
            # Create secure action tokens for this specific admin
            approve_token = create_action_token(
                data={
                    "application_id": application_id,
                    "admin_email": admin_email,
                    "action": "approve"
                },
                expires_delta=timedelta(days=7)
            )
            
            reject_token = create_action_token(
                data={
                    "application_id": application_id,
                    "admin_email": admin_email,
                    "action": "reject"
                },
                expires_delta=timedelta(days=7)
            )
            
            # Generate personalized email content
            html_content = get_admin_engineer_application_template(
                f"{engineer.first_name} {engineer.last_name}",
                engineer.email,
                application_id,
                approve_token=approve_token,
                reject_token=reject_token
            )
            
            # Send individual email
            result = email_service.send_email(
                to_email=admin_email,
                subject=subject,
                html_content=html_content
            )
            results.append(result)
        
        return any(results)
    except Exception as e:
        logger.error(f"Failed to send engineer application notification: {e}")
        return False


async def send_engineer_approval_notification(engineer: User) -> bool:
    """Send engineer approval notification."""
    try:
        subject = "Engineer Application Approved - Poornasree AI"
        html_content = get_engineer_approval_template(engineer.first_name)
        
        return email_service.send_email(
            to_email=engineer.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send engineer approval email to {engineer.email}: {e}")
        return False


async def send_engineer_rejection_notification(engineer: User, reason: str = "") -> bool:
    """Send engineer rejection notification."""
    try:
        subject = "Engineer Application Update - Poornasree AI"
        html_content = get_engineer_rejection_template(engineer.first_name, reason)
        
        return email_service.send_email(
            to_email=engineer.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send engineer rejection email to {engineer.email}: {e}")
        return False


async def send_notification_email(user: User, notification_type: NotificationType, content: str) -> bool:
    """Send general notification email."""
    try:
        subject_map = {
            NotificationType.VERIFICATION: "Email Verification",
            NotificationType.OTP: "OTP Verification", 
            NotificationType.WELCOME: "Welcome",
            NotificationType.ENGINEER_APPLICATION: "Engineer Application",
            NotificationType.ENGINEER_APPROVED: "Application Approved",
            NotificationType.ENGINEER_REJECTED: "Application Update",
            NotificationType.GENERAL: "Notification"
        }
        
        subject = f"{subject_map.get(notification_type, 'Notification')} - Poornasree AI"
        
        html_content = f"""
        <h2>{subject}</h2>
        <p>Hello {user.first_name},</p>
        <div>{content}</div>
        <p>Best regards,<br>Poornasree AI Team</p>
        """
        
        return email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send notification email to {user.email}: {e}")
        return False
