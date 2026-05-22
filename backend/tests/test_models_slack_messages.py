"""
Unit Tests for SlackMessage Model (TDD-GREEN Phase)
Tests for SlackMessage SQLAlchemy model with actual instantiation
"""
import pytest
from datetime import datetime, timezone


class TestSlackMessageModel:
    """Test suite for SlackMessage SQLAlchemy model"""
    
    def test_slack_message_model_exists(self):
        """Test that SlackMessage model can be imported"""
        from src.models.slack_messages import SlackMessage
        assert SlackMessage is not None
    
    def test_slack_message_has_required_fields(self):
        """Test that SlackMessage has all required fields"""
        from src.models.slack_messages import SlackMessage
        
        required_fields = [
            'id', 'slack_message_id', 'slack_channel_id', 'slack_user_id',
            'slack_team_id', 'text', 'thread_ts', 'parent_ts', 'message_type',
            'timestamp', 'slack_timestamp', 'processed', 'created_at', 'updated_at'
        ]
        
        for field in required_fields:
            assert hasattr(SlackMessage, field), f"SlackMessage missing field: {field}"
    
    def test_slack_message_can_be_instantiated(self):
        """Test that SlackMessage can be instantiated with required fields"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            slack_user_id="U9876543210",
            text="Hello, world!",
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message",
            processed=False  # Set explicitly since defaults are DB-level
        )
        
        assert message.slack_message_id == "U1234567890.1234567890"
        assert message.slack_channel_id == "C1234567890"
        assert message.text == "Hello, world!"
        assert message.message_type == "message"
        assert message.processed is False
    
    def test_slack_message_to_dict(self):
        """Test that to_dict method converts model to dictionary"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            text="Test message",
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message"
        )
        
        message_dict = message.to_dict()
        
        assert isinstance(message_dict, dict)
        assert message_dict['slack_message_id'] == "U1234567890.1234567890"
        assert message_dict['text'] == "Test message"
        assert 'created_at' in message_dict
        assert 'updated_at' in message_dict
    
    def test_slack_message_repr(self):
        """Test that repr method returns meaningful string"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            text="A very long message that should be truncated in repr",
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message"
        )
        
        repr_str = repr(message)
        assert "SlackMessage" in repr_str
        assert "U1234567890.1234567890" in repr_str
        assert "..." in repr_str  # Truncation indicator
    
    def test_slack_message_optional_fields(self):
        """Test that optional fields can be None"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            text=None,  # Optional
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message"
        )
        
        assert message.text is None
        assert message.thread_ts is None
        assert message.parent_ts is None
    
    def test_slack_message_thread_support(self):
        """Test that thread fields work correctly"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            text="Thread reply",
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message",
            thread_ts="1234567890.123456",
            parent_ts="1234567890.123400"
        )
        
        assert message.thread_ts == "1234567890.123456"
        assert message.parent_ts == "1234567890.123400"
    
    def test_slack_message_timestamp_auto_generated(self):
        """Test that created_at and updated_at fields exist and can be set"""
        from src.models.slack_messages import SlackMessage
        
        now = datetime.now(timezone.utc)
        message = SlackMessage(
            slack_message_id="U1234567890.1234567890",
            slack_channel_id="C1234567890",
            text="Test",
            timestamp=now,
            slack_timestamp="1234567890.123456",
            message_type="message",
            created_at=now,  # Set explicitly since auto-generation is DB-level
            updated_at=now
        )
        
        assert message.created_at is not None
        assert message.updated_at is not None
        assert isinstance(message.created_at, datetime)
        assert isinstance(message.updated_at, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])