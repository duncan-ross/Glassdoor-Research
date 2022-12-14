"""empty message

Revision ID: cb24ae961a3b
Revises: 0f36539ad38e
Create Date: 2017-08-01 22:31:05.324830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb24ae961a3b'
down_revision = '0f36539ad38e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('company_financials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('ticker', sa.String(), nullable=True),
    sa.Column('monthly_price_high', sa.Float(), nullable=True),
    sa.Column('monthly_price_low', sa.Float(), nullable=True),
    sa.Column('monthly_price_close', sa.Float(), nullable=True),
    sa.Column('total_return_factor', sa.Float(), nullable=True),
    sa.Column('data_date', sa.Date(), nullable=True),
    sa.Column('next_data_date', sa.Date(), nullable=True),
    sa.Column('ipo_date', sa.Date(), nullable=True),
    sa.Column('ipo_open_price', sa.Float(), nullable=True),
    sa.Column('ipo_fd_close_price', sa.Float(), nullable=True),
    sa.Column('quarter', sa.Integer(), nullable=True),
    sa.Column('dollar_change_quarterly', sa.Float(), nullable=True),
    sa.Column('pct_change_quarterly', sa.Float(), nullable=True),
    sa.Column('pct_change_from_ipo', sa.Float(), nullable=True),
    sa.Column('pct_change_from_fd_close', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], [u'companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('company_financials')
    # ### end Alembic commands ###
