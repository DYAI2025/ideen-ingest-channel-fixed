"""
SlackMessage SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class SlackMessage(Base, TimestampMixin):
    """SQLAlchemy Model for Slack Messages"""
    __tablename__ = 'slack_messages'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Slack Identifiers
    slack_message_id = Column(String(50), unique=True, nullable=False, index=True)
    slack_channel_id = Column(String(50), nullable=False, index=True)
    slack_user_id = Column(String(50), nullable=True, index=True)
    slack_team_id = Column(String(50), nullable=True)
    
    # Message Content
    text = Column(Text, nullable=True)
    thread_ts = Column(String(50), nullable=True)
    parent_ts = Column(String(50), nullable=True)
    message_type = Column(String(20), default='message', nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    slack_timestamp = Column(String(50), nullable=False)
    
    # Processing Status
    processed = Column(Boolean, default=False, nullable=False, index=True)
    
    # Relationships (to be implemented later)
    # files = relationship("SlackFile", back_populates="message")
    # user = relationship("SlackUser", back_populates="messages")
    # channel = relationship("SlackChannel", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_slack_channel_timestamp', 'slack_channel_id', 'timestamp'),
        Index('idx_processed_timestamp', 'processed', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SlackMessage(id={self.id}, slack_message_id='{self.slack_message_id}', text='{self.text[:50] if self.text else None}...')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slack_message_id': self.slack_message_id,
            'slack_channel_id': self.slack_channel_id,
            'slack_user_id': self.slack_user_id,
            'slack_team_id': self.slack_team_id,
            'text': self.text,
            'thread_ts': self.thread_ts,
            'parent_ts': self.parent_ts,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'slack_timestamp': self.slack_timestamp,
            'processed': self.processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }