"""added foreignkey to driver table schema

Revision ID: 88647e7459e8
Revises: 97d3d55bc423
Create Date: 2024-09-26 16:54:41.792668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88647e7459e8'
down_revision: Union[str, None] = '97d3d55bc423'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'drivers', 'vehicles', ['assigned_vehicle_id'], ['vehicle_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'drivers', type_='foreignkey')
    # ### end Alembic commands ###
