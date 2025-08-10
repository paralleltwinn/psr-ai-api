# =============================================================================
# POORNASREE AI - DATABASE MODELS
# =============================================================================

"""
SQLAlchemy database models for the authentication system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from ..core.constants import UserRole, UserStatus


class User(Base):
    """User model representing all user types in the system."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OTP-only users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0)
    
    # OTP related fields
    otp_secret = Column(String(255), nullable=True)
    
    # Profile fields
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    
    # Customer specific fields
    machine_model = Column(String(200), nullable=True)
    state = Column(String(100), nullable=True)
    
    # Engineer specific fields
    department = Column(String(100), nullable=True)
    dealer = Column(String(200), nullable=True)
    
    # Relationships
    notifications_sent = relationship(
        "Notification", 
        foreign_keys="Notification.sender_id", 
        back_populates="sender"
    )
    notifications_received = relationship(
        "Notification", 
        foreign_keys="Notification.recipient_id", 
        back_populates="recipient"
    )
    engineer_applications = relationship(
        "EngineerApplication",
        foreign_keys="EngineerApplication.user_id",
        back_populates="user"
    )
    reviewed_applications = relationship(
        "EngineerApplication",
        foreign_keys="EngineerApplication.reviewed_by",
        back_populates="reviewer"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class OTPVerification(Base):
    """OTP verification model for temporary codes."""
    
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), nullable=False, index=True)
    otp_code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)  # login, registration, etc.
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OTPVerification(id={self.id}, email='{self.email}', purpose='{self.purpose}')>"


class Notification(Base):
    """Notification model for in-app notifications."""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Additional metadata
    metadata_json = Column(Text, nullable=True)  # For storing additional data as JSON
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="notifications_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="notifications_received")

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', recipient_id={self.recipient_id})>"


class EngineerApplication(Base):
    """Engineer application model for approval workflow."""
    
    __tablename__ = "engineer_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Application details
    department = Column(String(100), nullable=True)
    experience = Column(String(50), nullable=True)  # e.g., "5 years", "10+ years"
    skills = Column(Text, nullable=True)
    portfolio = Column(String(500), nullable=True)
    cover_letter = Column(Text, nullable=True)
    
    # Application status and review
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Alias for compatibility
    review_notes = Column(Text, nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)  # Alias for compatibility
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="engineer_applications")
    reviewer = relationship("User", foreign_keys=[reviewed_by], back_populates="reviewed_applications")

    def __repr__(self):
        return f"<EngineerApplication(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class AuditLog(Base):
    """Audit log model for tracking important actions."""
    
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # user, application, etc.
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"


class LoginAttempt(Base):
    """Login attempt model for security tracking."""
    
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500), nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LoginAttempt(id={self.id}, email='{self.email}', success={self.success})>"


class ChatConversation(Base):
    """Chat conversation model for storing chat sessions."""
    
    __tablename__ = "chat_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatConversation(id={self.id}, conversation_id='{self.conversation_id}', user_id={self.user_id})>"


class ChatMessage(Base):
    """Chat message model for storing individual messages."""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), ForeignKey("chat_conversations.conversation_id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON string of sources
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, conversation_id='{self.conversation_id}', role='{self.role}')>"
