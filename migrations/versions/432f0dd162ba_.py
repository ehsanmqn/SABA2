"""empty message

Revision ID: 432f0dd162ba
Revises: 
Create Date: 2020-04-18 22:30:37.871111

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '432f0dd162ba'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analytics', sa.Column('longitude', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analytics', 'longitude')
    # ### end Alembic commands ###
