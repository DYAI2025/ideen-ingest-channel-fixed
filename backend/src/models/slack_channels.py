"""
SlackChannel SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class SlackChannel(Base, TimestampMixin):
    """SQLAlchemy Model for Slack Channels"""
    __tablename__ = 'slack_channels'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Slack Identifiers
    slack_channel_id = Column(String(50), unique=True, nullable=False, index=True)
    slack_team_id = Column(String(50), nullable=True)
    
    # Channel Information
    channel_name = Column(String(100), nullable=True)
    channel_type = Column(String(20), nullable=True)  # 'public', 'private', 'mpim', 'im'
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Configuration
    category = Column(String(50), nullable=True, index=True)  # 'ideas', 'general', 'projects', etc.
    auto_process = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships (to be implemented later)
    # messages = relationship("SlackMessage", back_populates="channel")
    
    # Indexes
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_auto_process', 'auto_process'),
    )
    
    def __repr__(self):
        return f"<SlackChannel(id={self.id}, slack_channel_id='{self.slack_channel_id}', channel_name='{self.channel_name}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slack_channel_id': self.slack_channel_id,
            'slack_team_id': self.slack_team_id,
            'channel_name': self.channel_name,
            'channel_type': self.channel_type,
            'is_archived': self.is_archived,
            'category': self.category,
            'auto_process': self.auto_process,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }