"""
Unit Tests for SlackFile Model (TDD-GREEN Phase)
Tests for SlackFile SQLAlchemy model with actual instantiation
"""
import pytest


class TestSlackFileModel:
    """Test suite for SlackFile SQLAlchemy model"""
    
    def test_slack_file_model_exists(self):
        """Test that SlackFile model can be imported"""
        from src.models.slack_files import SlackFile
        assert SlackFile is not None
    
    def test_slack_file_has_required_fields(self):
        """Test that SlackFile has all required fields"""
        from src.models.slack_files import SlackFile
        
        required_fields = [
            'id', 'slack_file_id', 'slack_message_id', 'file_name', 'file_url',
            'size_bytes', 'mime_type', 'file_type', 'downloaded', 'created_at', 'updated_at'
        ]
        
        for field in required_fields:
            assert hasattr(SlackFile, field), f"SlackFile missing field: {field}"
    
    def test_slack_file_can_be_instantiated(self):
        """Test that SlackFile can be instantiated with required fields"""
        from src.models.slack_files import SlackFile
        
        file_obj = SlackFile(
            slack_file_id="F1234567890",
            slack_message_id="U1234567890.1234567890",
            file_name="test.pdf",
            file_url="https://files.slack.com/files/test.pdf",
            size_bytes=1024,
            mime_type="application/pdf",
            downloaded=False  # Set explicitly since defaults are DB-level
        )
        
        assert file_obj.slack_file_id == "F1234567890"
        assert file_obj.slack_message_id == "U1234567890.1234567890"
        assert file_obj.file_name == "test.pdf"
        assert file_obj.size_bytes == 1024
        assert file_obj.downloaded is False
    
    def test_slack_file_to_dict(self):
        """Test that to_dict method converts model to dictionary"""
        from src.models.slack_files import SlackFile
        
        file_obj = SlackFile(
            slack_file_id="F1234567890",
            slack_message_id="U1234567890.1234567890",
            file_name="test.pdf",
            file_url="https://files.slack.com/files/test.pdf",
            size_bytes=1024
        )
        
        file_dict = file_obj.to_dict()
        
        assert isinstance(file_dict, dict)
        assert file_dict['slack_file_id'] == "F1234567890"
        assert file_dict['file_name'] == "test.pdf"
        assert 'created_at' in file_dict
        assert 'updated_at' in file_dict
    
    def test_slack_file_repr(self):
        """Test that repr method returns meaningful string"""
        from src.models.slack_files import SlackFile
        
        file_obj = SlackFile(
            slack_file_id="F1234567890",
            slack_message_id="U1234567890.1234567890",
            file_name="test.pdf"
        )
        
        repr_str = repr(file_obj)
        assert "SlackFile" in repr_str
        assert "F1234567890" in repr_str
        assert "test.pdf" in repr_str
    
    def test_slack_file_optional_fields(self):
        """Test that optional fields can be None"""
        from src.models.slack_files import SlackFile
        
        file_obj = SlackFile(
            slack_file_id="F1234567890",
            slack_message_id="U1234567890.1234567890",
            file_name=None,  # Optional
            file_url=None,  # Optional
            size_bytes=None  # Optional
        )
        
        assert file_obj.file_name is None
        assert file_obj.file_url is None
        assert file_obj.size_bytes is None
    
    def test_slack_file_download_status(self):
        """Test that download status field works correctly"""
        from src.models.slack_files import SlackFile
        
        file_obj = SlackFile(
            slack_file_id="F1234567890",
            slack_message_id="U1234567890.1234567890",
            file_name="test.pdf",
            downloaded=True
        )
        
        assert file_obj.downloaded is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])