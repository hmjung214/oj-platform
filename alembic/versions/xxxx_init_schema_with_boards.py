from alembic import op
import sqlalchemy as sa

revision = 'xxxx_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
    )

    op.create_table(
        'problems',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
    )

    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('problem_id', sa.Integer, sa.ForeignKey('problems.id')),
        sa.Column('code', sa.Text, nullable=False),
    )

    op.create_table(
        'boards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(255)),
        sa.Column('list_level', sa.Integer, default=1),
        sa.Column('view_level', sa.Integer, default=1),
        sa.Column('write_level', sa.Integer, default=1),
        sa.Column('reply_level', sa.Integer, default=1),
        sa.Column('comment_level', sa.Integer, default=1),
        sa.Column('link_level', sa.Integer, default=1),
        sa.Column('upload_level', sa.Integer, default=1),
        sa.Column('download_level', sa.Integer, default=1),
        sa.Column('html_level', sa.Integer, default=1),
        sa.Column('use_secret', sa.String(20), default='none'),
        sa.Column('use_dhtml', sa.Boolean, default=False),
        sa.Column('upload_count', sa.Integer, default=2),
        sa.Column('upload_size', sa.Integer, default=1048576),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('boards')
    op.drop_table('submissions')
    op.drop_table('problems')
    op.drop_table('users')
