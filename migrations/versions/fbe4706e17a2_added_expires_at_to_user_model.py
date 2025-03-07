from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

# Revision identifiers, used by Alembic.
revision = 'fbe4706e17a2'
down_revision = '5e5de586659c'
branch_labels = None
depends_on = None

def upgrade():
    # Set a default value for existing rows (current time + 28 days)
    default_expiry = datetime.utcnow() + timedelta(days=28)

    # Add expires_at column with a default value
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(), nullable=False, server_default=sa.text(f"'{default_expiry.isoformat()}'")))

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('expires_at')
