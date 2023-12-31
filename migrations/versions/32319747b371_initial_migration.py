"""Initial migration

Revision ID: 32319747b371
Revises: 
Create Date: 2023-08-01 20:05:35.159660

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32319747b371'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nom', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_column('nom')

    # ### end Alembic commands ###
