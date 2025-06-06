"""Add order_id to orders table

Revision ID: 9e6cf1a4b9ed
Revises: d63e3653cb44
Create Date: 2025-05-24 13:50:31.575714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9e6cf1a4b9ed'
down_revision = 'd63e3653cb44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order_id', sa.BigInteger(), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('address', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('total', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('order_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('shipping_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('delivery_status', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('delivery_date', sa.DateTime(), nullable=True))
        batch_op.drop_constraint('orders_email_key', type_='unique')
        batch_op.create_unique_constraint(None, ['order_id'])
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.drop_column('shipping_region')
        batch_op.drop_column('password')
        batch_op.drop_column('shipping_city')
        batch_op.drop_column('username')
        batch_op.drop_column('is_admin')
        batch_op.drop_column('avatar')
        batch_op.drop_column('shipping_address')
        batch_op.drop_column('shipping_country')
        batch_op.drop_column('email')
        batch_op.drop_column('shipping_name')
        batch_op.drop_column('shipping_phone')

    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('dark_mode', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('notifications_enabled', sa.Boolean(), nullable=True))
        batch_op.drop_constraint('user_settings_order_id_key', type_='unique')
        batch_op.drop_column('order_id')
        batch_op.drop_column('delivery_status')
        batch_op.drop_column('address')
        batch_op.drop_column('phone')
        batch_op.drop_column('delivery_date')
        batch_op.drop_column('payment_method')
        batch_op.drop_column('order_date')
        batch_op.drop_column('shipping_status')
        batch_op.drop_column('name')
        batch_op.drop_column('total')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
        batch_op.alter_column('avatar',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(length=255),
               existing_nullable=True)
        batch_op.drop_constraint('users_username_key', type_='unique')
        batch_op.drop_column('is_active')
        batch_op.drop_column('reset_token')
        batch_op.drop_column('reset_token_expiration')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token_expiration', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('reset_token', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.create_unique_constraint('users_username_key', ['username'], postgresql_nulls_not_distinct=False)
        batch_op.alter_column('avatar',
               existing_type=sa.String(length=255),
               type_=postgresql.BYTEA(),
               existing_nullable=True)
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)

    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('total', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('name', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('shipping_status', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('order_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('payment_method', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('delivery_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('phone', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('address', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('delivery_status', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('order_id', sa.BIGINT(), autoincrement=False, nullable=True))
        batch_op.create_unique_constraint('user_settings_order_id_key', ['order_id'], postgresql_nulls_not_distinct=False)
        batch_op.drop_column('notifications_enabled')
        batch_op.drop_column('dark_mode')
        batch_op.drop_column('language')

    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shipping_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('shipping_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('shipping_country', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('shipping_address', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('avatar', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('shipping_city', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('shipping_region', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('orders_email_key', ['email'], postgresql_nulls_not_distinct=False)
        batch_op.drop_column('delivery_date')
        batch_op.drop_column('delivery_status')
        batch_op.drop_column('shipping_status')
        batch_op.drop_column('order_date')
        batch_op.drop_column('total')
        batch_op.drop_column('address')
        batch_op.drop_column('phone')
        batch_op.drop_column('name')
        batch_op.drop_column('user_id')
        batch_op.drop_column('order_id')

    # ### end Alembic commands ###
