"""added default timestamps for created_at and updated_at fields

Revision ID: 1d0d259dac58
Revises: d43260ac4999
Create Date: 2024-09-24 17:48:07.578798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d0d259dac58'
down_revision: Union[str, None] = 'd43260ac4999'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
