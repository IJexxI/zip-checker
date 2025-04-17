from alembic import op
import sqlalchemy as sa

revision = 'd1c77138a2a4'
down_revision = '9adf51f9540a'

def upgrade():
    op.add_column('Uploads', sa.Column('file_content', sa.LargeBinary, nullable=True))

def downgrade():
    op.drop_column('Uploads', 'file_content')