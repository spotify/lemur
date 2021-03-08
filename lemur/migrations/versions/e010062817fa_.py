"""empty message

Revision ID: e010062817fa
Revises: c301c59688d2
Create Date: 2021-03-08 14:38:58.073056

"""

# revision identifiers, used by Alembic.
revision = 'e010062817fa'
down_revision = 'c301c59688d2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('endpoints', sa.Column('external_id', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('endpoints', 'external_id')
    # ### end Alembic commands ###