"""updated runner_performance table

Revision ID: c744d9011218
Revises: 06ddf4122e07
Create Date: 2023-01-14 14:38:18.669165

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c744d9011218'
down_revision = '06ddf4122e07'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('runner_performance', sa.Column('relays_last_48_hours', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('relays_last_24_hours', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('relays_last_6_hours', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('serviced_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('serviced_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('serviced_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_rewards_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_rewards_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_rewards_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_relays_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_relays_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_relays_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_base_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_base_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_base_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_total_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_total_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_total_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_producer_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_producer_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('avg_producer_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_times_last_48_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_times_last_24_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('producer_times_last_6_hours', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_tokens_staked', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_validator_tokens_staked', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('validators', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('last_height', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_pending_relays', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_estimated_pending_rewards', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('jailed_now', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_balance', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('total_output_balance', sa.DECIMAL(), nullable=False))
    op.add_column('runner_performance', sa.Column('nodes_staked', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('nodes_unstaked', sa.BigInteger(), nullable=False))
    op.add_column('runner_performance', sa.Column('nodes_unstaking', sa.BigInteger(), nullable=False))
    op.drop_column('runner_performance', 'updated_at')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('runner_performance', sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.drop_column('runner_performance', 'nodes_unstaking')
    op.drop_column('runner_performance', 'nodes_unstaked')
    op.drop_column('runner_performance', 'nodes_staked')
    op.drop_column('runner_performance', 'total_output_balance')
    op.drop_column('runner_performance', 'total_balance')
    op.drop_column('runner_performance', 'jailed_now')
    op.drop_column('runner_performance', 'total_estimated_pending_rewards')
    op.drop_column('runner_performance', 'total_pending_relays')
    op.drop_column('runner_performance', 'last_height')
    op.drop_column('runner_performance', 'validators')
    op.drop_column('runner_performance', 'total_validator_tokens_staked')
    op.drop_column('runner_performance', 'total_tokens_staked')
    op.drop_column('runner_performance', 'producer_times_last_6_hours')
    op.drop_column('runner_performance', 'producer_times_last_24_hours')
    op.drop_column('runner_performance', 'producer_times_last_48_hours')
    op.drop_column('runner_performance', 'avg_producer_last_6_hours')
    op.drop_column('runner_performance', 'avg_producer_last_24_hours')
    op.drop_column('runner_performance', 'avg_producer_last_48_hours')
    op.drop_column('runner_performance', 'avg_total_last_6_hours')
    op.drop_column('runner_performance', 'avg_total_last_24_hours')
    op.drop_column('runner_performance', 'avg_total_last_48_hours')
    op.drop_column('runner_performance', 'avg_base_last_6_hours')
    op.drop_column('runner_performance', 'avg_base_last_24_hours')
    op.drop_column('runner_performance', 'avg_base_last_48_hours')
    op.drop_column('runner_performance', 'avg_relays_last_6_hours')
    op.drop_column('runner_performance', 'avg_relays_last_24_hours')
    op.drop_column('runner_performance', 'avg_relays_last_48_hours')
    op.drop_column('runner_performance', 'total_last_6_hours')
    op.drop_column('runner_performance', 'total_last_24_hours')
    op.drop_column('runner_performance', 'total_last_48_hours')
    op.drop_column('runner_performance', 'producer_rewards_last_6_hours')
    op.drop_column('runner_performance', 'producer_rewards_last_24_hours')
    op.drop_column('runner_performance', 'producer_rewards_last_48_hours')
    op.drop_column('runner_performance', 'serviced_last_6_hours')
    op.drop_column('runner_performance', 'serviced_last_24_hours')
    op.drop_column('runner_performance', 'serviced_last_48_hours')
    op.drop_column('runner_performance', 'relays_last_6_hours')
    op.drop_column('runner_performance', 'relays_last_24_hours')
    op.drop_column('runner_performance', 'relays_last_48_hours')
    # ### end Alembic commands ###
