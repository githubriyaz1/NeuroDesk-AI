"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-01 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)

    # 3. assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_type', sa.String(length=50), nullable=False, server_default='DOCUMENT'),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('extension', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('storage_provider', sa.String(length=50), nullable=False, server_default='local'),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='CREATED'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assets_owner_id'), 'assets', ['owner_id'], unique=False)
    op.create_index(op.f('ix_assets_asset_type'), 'assets', ['asset_type'], unique=False)
    op.create_index(op.f('ix_assets_status'), 'assets', ['status'], unique=False)
    op.create_index(op.f('ix_assets_is_favorite'), 'assets', ['is_favorite'], unique=False)
    op.create_index(op.f('ix_assets_is_deleted'), 'assets', ['is_deleted'], unique=False)
    op.create_index('idx_assets_owner_deleted', 'assets', ['owner_id', 'is_deleted'], unique=False)
    op.create_index('idx_assets_owner_favorite', 'assets', ['owner_id', 'is_favorite'], unique=False)
    op.create_index('idx_assets_owner_type', 'assets', ['owner_id', 'asset_type'], unique=False)

    # 4. asset_metadata table
    op.create_table(
        'asset_metadata',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('asset_id', sa.UUID(), nullable=False),
        sa.Column('metadata_key', sa.String(length=100), nullable=False),
        sa.Column('metadata_value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(length=50), nullable=False, server_default='string'),
        sa.Column('extracted_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_metadata_asset_id'), 'asset_metadata', ['asset_id'], unique=False)
    op.create_index(op.f('ix_asset_metadata_metadata_key'), 'asset_metadata', ['metadata_key'], unique=False)
    op.create_index('idx_asset_metadata_asset_key', 'asset_metadata', ['asset_id', 'metadata_key'], unique=True)


def downgrade() -> None:
    op.drop_table('asset_metadata')
    op.drop_table('assets')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
