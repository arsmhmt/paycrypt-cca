"""add payment sessions table

Revision ID: 20250814_add_payment_sessions
Revises: 71c4805a70ba
Create Date: 2025-08-14
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250814_add_payment_sessions'
down_revision = '71c4805a70ba'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'payment_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('public_id', sa.String(length=32), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(18, 2), nullable=False),
        sa.Column('currency', sa.String(length=5), nullable=False),
        sa.Column('customer_email', sa.String(length=255), nullable=True),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('success_url', sa.Text(), nullable=False),
        sa.Column('cancel_url', sa.Text(), nullable=False),
        sa.Column('webhook_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id']),
    )
    op.create_index('ix_payment_sessions_public_id', 'payment_sessions', ['public_id'], unique=True)
    op.create_index('ix_payment_sessions_client_id', 'payment_sessions', ['client_id'], unique=False)
    op.create_index('ix_payment_sessions_order_id', 'payment_sessions', ['order_id'], unique=False)


def downgrade():
    op.drop_index('ix_payment_sessions_order_id', table_name='payment_sessions')
    op.drop_index('ix_payment_sessions_client_id', table_name='payment_sessions')
    op.drop_index('ix_payment_sessions_public_id', table_name='payment_sessions')
    op.drop_table('payment_sessions')
