"""empty message

Revision ID: 973533b1d7bd
Revises: c301c59688d2
Create Date: 2021-03-02 19:31:49.649293

"""

# revision identifiers, used by Alembic.
revision = '973533b1d7bd'
down_revision = 'c301c59688d2'

from alembic import op
import sqlalchemy as sa


certificate_destination_state = sa.Enum('PENDING', 'FAILED', 'UPLOADED', name='certificate_destination_state')


def upgrade():
    certificate_destination_state.create(op.get_bind())
    op.add_column('certificate_destination_associations',
                  sa.Column('state',
                            certificate_destination_state,
                            nullable=False,
                            server_default='PENDING'))


def downgrade():
    op.drop_column('certificate_destination_associations', 'state')
    certificate_destination_state.drop(op.get_bind())
