"""add tasks table

Revision ID: 001_add_tasks
Revises:
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_tasks'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add tasks table and update assignments table."""

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_tasks_assignment_id'), 'tasks', ['assignment_id'], unique=False)
    op.create_index(op.f('ix_tasks_due_date'), 'tasks', ['due_date'], unique=False)
    op.create_index(op.f('ix_tasks_is_completed'), 'tasks', ['is_completed'], unique=False)

    # Add columns to assignments table
    op.add_column('assignments', sa.Column('tasks_generated', sa.Boolean(), nullable=True))
    op.add_column('assignments', sa.Column('tasks_generated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """Remove tasks table and assignment columns."""

    # Remove assignment columns
    op.drop_column('assignments', 'tasks_generated_at')
    op.drop_column('assignments', 'tasks_generated')

    # Drop indexes
    op.drop_index(op.f('ix_tasks_is_completed'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_due_date'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_assignment_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')

    # Drop table
    op.drop_table('tasks')
