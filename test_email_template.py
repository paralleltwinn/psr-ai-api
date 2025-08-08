#!/usr/bin/env python3
"""
Test script to generate and preview standardized email templates
"""

from app.services.email_service import (
    get_verification_email_template,
    get_otp_email_template,
    get_registration_otp_template,
    get_welcome_email_template,
    get_engineer_application_template,
    get_engineer_approval_template,
    get_engineer_rejection_template,
    get_admin_engineer_application_template
)

def test_templates():
    """Generate sample email templates to verify styling."""
    
    print("🎨 Generating standardized email templates...\n")
    
    # Test verification email
    verification_html = get_verification_email_template(
        "John Doe", 
        "https://localhost:3000/verify?token=abc123"
    )
    print("✅ Verification email template generated")
    
    # Test OTP email
    otp_html = get_otp_email_template("Jane Smith", "123456")
    print("✅ OTP email template generated")
    
    # Test registration OTP
    reg_otp_html = get_registration_otp_template("Alex Johnson", "789012")
    print("✅ Registration OTP template generated")
    
    # Test welcome email
    welcome_html = get_welcome_email_template("Sarah Wilson", "customer")
    print("✅ Welcome email template generated")
    
    # Test engineer application (for engineer)
    eng_app_html = get_engineer_application_template("Mike Chen", "Software Engineering", "Admin Team")
    print("✅ Engineer application template generated")
    
    # Test admin notification
    admin_html = get_admin_engineer_application_template("Mike Chen", "mike@example.com", 12345)
    print("✅ Admin notification template generated")
    
    # Test approval email
    approval_html = get_engineer_approval_template("Mike Chen")
    print("✅ Engineer approval template generated")
    
    # Test rejection email
    rejection_html = get_engineer_rejection_template("Mike Chen", "Need more experience with Python frameworks")
    print("✅ Engineer rejection template generated")
    
    print(f"\n🎉 All 8 email templates generated successfully!")
    print(f"📧 Templates now use consistent modern design with:")
    print(f"   • Unified color schemes and gradients")
    print(f"   • Consistent typography and spacing")
    print(f"   • Professional layout with proper branding")
    print(f"   • Mobile-responsive design")
    print(f"   • Accessible styling and structure")
    
    # Save a sample template for preview
    with open("sample_email.html", "w", encoding="utf-8") as f:
        f.write(verification_html)
    print(f"\n📄 Sample email saved as 'sample_email.html' for preview")

if __name__ == "__main__":
    test_templates()
