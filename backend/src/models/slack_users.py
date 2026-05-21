"""
SlackUser SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class SlackUser(Base, TimestampMixin):
    """SQLAlchemy Model for Slack Users"""
    __tablename__ = 'slack_users'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Slack Identifiers
    slack_user_id = Column(String(50), unique=True, nullable=False, index=True)
    slack_team_id = Column(String(50), nullable=True)
    
    # User Information
    username = Column(String(100), nullable=True, index=True)
    display_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    is_bot = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    
    # Relationships (to be implemented later)
    # messages = relationship("SlackMessage", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_username', 'username'),
    )
    
    def __repr__(self):
        return f"<SlackUser(id={self.id}, slack_user_id='{self.slack_user_id}', username='{self.username}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slack_user_id': self.slack_user_id,
            'slack_team_id': self.slack_team_id,
            'username': self.username,
            'display_name': self.display_name,
            'email': self.email,
            'is_bot': self.is_bot,
            'is_admin': self.is_admin,
            'profile_image_url': self.profile_image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }