"""empty message

Revision ID: cbf0f1a773c4
Revises: 26f97d447c2d
Create Date: 2020-04-02 11:08:53.457664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbf0f1a773c4'
down_revision = '26f97d447c2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('IndicatorValue', sa.Column('def_value', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('IndicatorValue', 'def_value')
    # ### end Alembic commands ###
