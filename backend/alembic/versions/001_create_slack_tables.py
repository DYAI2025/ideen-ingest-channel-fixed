"""Create Slack tables

Revision ID: 001_create_slack_tables
Revises: 
Create Date: 2026-05-21 04:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_create_slack_tables'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create slack_users table
    op.create_table(
        'slack_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slack_user_id', sa.String(length=50), nullable=False),
        sa.Column('slack_team_id', sa.String(length=50), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_bot', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slack_user_id')
    )
    op.create_index('ix_slack_users_slack_user_id', 'slack_users', ['slack_user_id'], unique=True)
    op.create_index('ix_slack_users_username', 'slack_users', ['username'], unique=False)

    # Create slack_channels table
    op.create_table(
        'slack_channels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slack_channel_id', sa.String(length=50), nullable=False),
        sa.Column('slack_team_id', sa.String(length=50), nullable=True),
        sa.Column('channel_name', sa.String(length=100), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_archived', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slack_channel_id')
    )
    op.create_index('ix_slack_channels_slack_channel_id', 'slack_channels', ['slack_channel_id'], unique=True)

    # Create slack_messages table
    op.create_table(
        'slack_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slack_message_id', sa.String(length=50), nullable=False),
        sa.Column('slack_channel_id', sa.String(length=50), nullable=False),
        sa.Column('slack_user_id', sa.String(length=50), nullable=True),
        sa.Column('slack_team_id', sa.String(length=50), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('thread_ts', sa.String(length=50), nullable=True),
        sa.Column('parent_ts', sa.String(length=50), nullable=True),
        sa.Column('message_type', sa.String(length=20), nullable=False, default='message'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('slack_timestamp', sa.String(length=50), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slack_message_id')
    )
    op.create_index('ix_slack_messages_slack_message_id', 'slack_messages', ['slack_message_id'], unique=True)
    op.create_index('ix_slack_messages_slack_channel_id', 'slack_messages', ['slack_channel_id'], unique=False)
    op.create_index('ix_slack_messages_slack_user_id', 'slack_messages', ['slack_user_id'], unique=False)
    op.create_index('ix_slack_messages_timestamp', 'slack_messages', ['timestamp'], unique=False)
    op.create_index('ix_slack_messages_processed', 'slack_messages', ['processed'], unique=False)
    op.create_index('idx_slack_channel_timestamp', 'slack_messages', ['slack_channel_id', 'timestamp'], unique=False)
    op.create_index('idx_processed_timestamp', 'slack_messages', ['processed', 'timestamp'], unique=False)

    # Create slack_files table
    op.create_table(
        'slack_files',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slack_file_id', sa.String(length=50), nullable=False),
        sa.Column('slack_message_id', sa.String(length=50), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('downloaded', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slack_file_id')
    )
    op.create_index('ix_slack_files_slack_file_id', 'slack_files', ['slack_file_id'], unique=True)
    op.create_index('ix_slack_files_slack_message_id', 'slack_files', ['slack_message_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_slack_files_slack_message_id', table_name='slack_files')
    op.drop_index('ix_slack_files_slack_file_id', table_name='slack_files')
    op.drop_table('slack_files')

    op.drop_index('idx_processed_timestamp', table_name='slack_messages')
    op.drop_index('idx_slack_channel_timestamp', table_name='slack_messages')
    op.drop_index('ix_slack_messages_processed', table_name='slack_messages')
    op.drop_index('ix_slack_messages_timestamp', table_name='slack_messages')
    op.drop_index('ix_slack_messages_slack_user_id', table_name='slack_messages')
    op.drop_index('ix_slack_messages_slack_channel_id', table_name='slack_messages')
    op.drop_index('ix_slack_messages_slack_message_id', table_name='slack_messages')
    op.drop_table('slack_messages')

    op.drop_index('ix_slack_channels_slack_channel_id', table_name='slack_channels')
    op.drop_table('slack_channels')

    op.drop_index('ix_slack_users_username', table_name='slack_users')
    op.drop_index('ix_slack_users_slack_user_id', table_name='slack_users')
    op.drop_table('slack_users')