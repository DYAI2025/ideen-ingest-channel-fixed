"""
SlackFile SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class SlackFile(Base, TimestampMixin):
    """SQLAlchemy Model for Slack Files"""
    __tablename__ = 'slack_files'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Slack Identifiers
    slack_file_id = Column(String(50), unique=True, nullable=False, index=True)
    slack_message_id = Column(String(50), nullable=False, index=True)
    
    # File Information
    file_name = Column(String(255), nullable=True)
    file_url = Column(String(500), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_type = Column(String(50), nullable=True)
    
    # Download Status
    downloaded = Column(Boolean, default=False, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_slack_message_id', 'slack_message_id'),
        Index('idx_downloaded', 'downloaded'),
    )
    
    def __repr__(self):
        return f"<SlackFile(id={self.id}, slack_file_id='{self.slack_file_id}', file_name='{self.file_name}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slack_file_id': self.slack_file_id,
            'slack_message_id': self.slack_message_id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'size_bytes': self.size_bytes,
            'mime_type': self.mime_type,
            'file_type': self.file_type,
            'downloaded': self.downloaded,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }