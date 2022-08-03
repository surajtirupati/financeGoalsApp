"""empty message

Revision ID: e6b161e18b47
Revises: 
Create Date: 2022-06-24 16:36:39.634564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6b161e18b47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('userfinancialdata', sa.Column('disposable_income', sa.Float(), nullable=True))
    op.add_column('userfinancialdata', sa.Column('total_fixed_costs', sa.Float(), nullable=True))
    op.add_column('userfinancialdata', sa.Column('personal_income', sa.Float(), nullable=True))
    op.add_column('userfinancialdata', sa.Column('saving_income', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('userfinancialdata', 'saving_income')
    op.drop_column('userfinancialdata', 'personal_income')
    op.drop_column('userfinancialdata', 'total_fixed_costs')
    op.drop_column('userfinancialdata', 'disposable_income')
    # ### end Alembic commands ###
