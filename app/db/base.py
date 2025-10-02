from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Ensure models are imported so Alembic and metadata see them
from app.models import analytics as _analytics  # noqa: F401,E402
from app.models import position as _position  # noqa: F401,E402
