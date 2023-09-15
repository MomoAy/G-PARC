"""Ajout d'une colonne dans la table task

Revision ID: 9770b4f6f14f
Revises: 80d50c018567
Create Date: 2023-08-04 02:35:07.497395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9770b4f6f14f'
down_revision = '80d50c018567'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('statut', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('statut')

    # ### end Alembic commands ###
