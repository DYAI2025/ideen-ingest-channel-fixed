"""
SlackFile SQLAlchemy Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .base import Base, TimestampMixin


class SlackFile(Base, TimestampMixin):
    """SQLAlchemy Model for Slack Files"""
    __tablename__ = 'slack_files'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Slack Identifiers
    slack_file_id = Column(String(50), unique=True, nullable=False, index=True)
    slack_message_id = Column(Integer, ForeignKey('slack_messages.id'), nullable=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    mime_type = Column(String(100), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    
    # URLs
    url_private = Column(String(500), nullable=True)
    url_private_download = Column(String(500), nullable=True)
    
    # Storage Information
    storage_path = Column(String(500), nullable=True)
    downloaded = Column(Boolean, default=False, nullable=False, index=True)
    download_attempted_at = Column(DateTime(timezone=True), nullable=True)
    downloaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (to be implemented later)
    # message = relationship("SlackMessage", back_populates="files")
    
    # Indexes
    __table_args__ = (
        Index('idx_slack_message_id', 'slack_message_id'),
        Index('idx_downloaded', 'downloaded'),
    )
    
    def __repr__(self):
        return f"<SlackFile(id={self.id}, slack_file_id='{self.slack_file_id}', filename='{self.filename}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'slack_file_id': self.slack_file_id,
            'slack_message_id': self.slack_message_id,
            'filename': self.filename,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'url_private': self.url_private,
            'url_private_download': self.url_private_download,
            'storage_path': self.storage_path,
            'downloaded': self.downloaded,
            'download_attempted_at': self.download_attempted_at.isoformat() if self.download_attempted_at else None,
            'downloaded_at': self.downloaded_at.isoformat() if self.downloaded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }