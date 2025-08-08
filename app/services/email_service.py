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


def get_verification_email_template(user_name: str, verification_link: str) -> str:
    """Get HTML template for email verification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🚀 Poornasree AI</div>
            <h1>Welcome to Our Platform!</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name}!</h2>
            <p>Thank you for joining Poornasree AI. To complete your registration, please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center;">
                <a href="{verification_link}" class="button">Verify Email Address</a>
            </div>
            
            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px;">{verification_link}</p>
            
            <p><strong>Important:</strong> This verification link will expire in 24 hours for security reasons.</p>
            
            <p>If you didn't create an account with us, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </body>
    </html>
    """


def get_otp_email_template(user_name: str, otp_code: str) -> str:
    """Get HTML template for OTP verification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #007bff; text-align: center; background: white; padding: 20px; border-radius: 10px; margin: 20px 0; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🔐 Poornasree AI</div>
            <h1>OTP Verification</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name}!</h2>
            <p>You requested an OTP for verification. Please use the code below:</p>
            
            <div class="otp-code">{otp_code}</div>
            
            <p><strong>Important Security Information:</strong></p>
            <ul>
                <li>This OTP is valid for 10 minutes only</li>
                <li>Never share this code with anyone</li>
                <li>Our team will never ask for this code</li>
                <li>If you didn't request this, please contact support immediately</li>
            </ul>
            
            <p>If you didn't request this OTP, please ignore this email and ensure your account is secure.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </body>
    </html>
    """


def get_registration_otp_template(user_name: str, otp_code: str) -> str:
    """Get HTML template for registration OTP verification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Complete Registration - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #28a745; text-align: center; background: white; padding: 20px; border-radius: 10px; margin: 20px 0; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🚀 Poornasree AI</div>
            <h1>Complete Your Registration</h1>
        </div>
        <div class="content">
            <h2>Welcome {user_name}!</h2>
            <p>You're almost done! Please use the verification code below to complete your registration:</p>
            
            <div class="otp-code">{otp_code}</div>
            
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Enter this code in the registration form</li>
                <li>Complete your profile information</li>
                <li>Start exploring Poornasree AI features</li>
            </ul>
            
            <p><strong>Security Note:</strong> This code expires in 15 minutes for your security.</p>
            
            <p>If you didn't request this registration, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </body>
    </html>
    """


def get_welcome_email_template(user_name: str, user_role: str) -> str:
    """Get HTML template for welcome email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">🎉 Poornasree AI</div>
            <h1>Welcome Aboard!</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name}!</h2>
            <p>Congratulations! Your account has been successfully verified and activated.</p>
            
            <p><strong>Your Role:</strong> {user_role}</p>
            
            <h3>What's Next?</h3>
            <div class="feature">
                <strong>🏠 Dashboard Access:</strong> Explore your personalized dashboard with role-specific features
            </div>
            <div class="feature">
                <strong>🔧 Platform Features:</strong> Access all the tools and services available for your role
            </div>
            <div class="feature">
                <strong>📞 Support:</strong> Our team is here to help you get started
            </div>
            
            <p>We're excited to have you join our community and look forward to your journey with Poornasree AI!</p>
            
            <p>If you have any questions or need assistance, feel free to reach out to our support team.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>Need help? Contact our support team</p>
        </div>
    </body>
    </html>
    """


def get_engineer_application_template(engineer_name: str, engineer_email: str, application_id: int, admin_token: str = None) -> str:
    """Get HTML template for engineer application notification with approve/reject buttons."""
    
    # Base URLs for approve/reject actions
    base_url = settings.frontend_url or "http://localhost:3000"
    api_base_url = settings.api_base_url or "http://localhost:8000"
    
    # Create action URLs
    approve_url = f"{api_base_url}/admin/engineers/{application_id}/approve"
    reject_url = f"{api_base_url}/admin/engineers/{application_id}/reject"
    dashboard_url = f"{base_url}/dashboard"
    
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
            .approve-btn {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold; }}
            .reject-btn {{ display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 0 10px; font-weight: bold; }}
            .dashboard-btn {{ display: inline-block; background: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
            .urgent {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; }}
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
            <div class="action-buttons">
                <a href="{dashboard_url}" class="approve-btn">✅ APPROVE APPLICATION</a>
                <a href="{dashboard_url}" class="reject-btn">❌ REJECT APPLICATION</a>
            </div>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>💡 Quick Access:</strong> Click the buttons above to go directly to the admin dashboard where you can review detailed application information and take action.</p>
            </div>
            
            <h3>📝 Review Checklist:</h3>
            <ul style="background: white; padding: 20px; border-radius: 5px;">
                <li>✓ Verify applicant's email and contact information</li>
                <li>✓ Review submitted skills and experience</li>
                <li>✓ Check portfolio/work samples if provided</li>
                <li>✓ Evaluate department fit and requirements</li>
                <li>✓ Make approval/rejection decision</li>
            </ul>
            
            <div class="action-buttons">
                <a href="{dashboard_url}" class="dashboard-btn">🏠 Go to Admin Dashboard</a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                <strong>Note:</strong> For detailed applicant information and to complete the review process, please access your admin dashboard.
            </p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>Admin Notification System</p>
        </div>
    </body>
    </html>
    """


def get_engineer_approval_template(engineer_name: str) -> str:
    """Get HTML template for engineer approval notification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Engineer Application Approved - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .success-box {{ background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #c3e6cb; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">✅ Poornasree AI</div>
            <h1>Application Approved!</h1>
        </div>
        <div class="content">
            <h2>Congratulations {engineer_name}!</h2>
            
            <div class="success-box">
                <strong>🎉 Your Engineer application has been approved!</strong>
            </div>
            
            <p>We're excited to welcome you to our engineering team. Your application has been reviewed and approved by our administrators.</p>
            
            <h3>What's Next?</h3>
            <ul>
                <li>Your account has been upgraded to Engineer role</li>
                <li>You now have access to engineering features and tools</li>
                <li>Explore your new dashboard and capabilities</li>
                <li>Start collaborating with the team</li>
            </ul>
            
            <p>Welcome to the Poornasree AI engineering team! We look forward to your contributions.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>Engineering Team</p>
        </div>
    </body>
    </html>
    """


def get_engineer_rejection_template(engineer_name: str, reason: str = "") -> str:
    """Get HTML template for engineer rejection notification."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Engineer Application Update - Poornasree AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #dc3545 0%, #e83e5a 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .info-box {{ background: #f8d7da; color: #721c24; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #f5c6cb; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📋 Poornasree AI</div>
            <h1>Application Update</h1>
        </div>
        <div class="content">
            <h2>Hello {engineer_name},</h2>
            
            <div class="info-box">
                <strong>Application Status:</strong> Not approved at this time
            </div>
            
            <p>Thank you for your interest in joining our engineering team. After careful review, we have decided not to move forward with your application at this time.</p>
            
            {f'<p><strong>Feedback:</strong> {reason}</p>' if reason else ''}
            
            <p>We encourage you to:</p>
            <ul>
                <li>Continue developing your skills and experience</li>
                <li>Stay engaged with our platform as a customer</li>
                <li>Consider reapplying in the future</li>
            </ul>
            
            <p>We appreciate your interest in Poornasree AI and wish you the best in your career journey.</p>
        </div>
        <div class="footer">
            <p>© 2024 Poornasree AI. All rights reserved.</p>
            <p>Talent Acquisition Team</p>
        </div>
    </body>
    </html>
    """


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
    """Send engineer application notification to admins."""
    try:
        subject = "🚨 NEW Engineer Application - Immediate Review Required"
        html_content = get_engineer_application_template(
            f"{engineer.first_name} {engineer.last_name}",
            engineer.email,
            application_id
        )
        
        results = email_service.send_bulk_email(
            recipients=admin_emails,
            subject=subject,
            html_content=html_content
        )
        
        return any(results.values())
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
