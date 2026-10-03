from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


# This module defines the application's database tables as SQLAlchemy ORM models.
# Each class that inherits from Base maps Python objects to rows in a database table.
class User(Base):
    """Represents a registered user stored in the users database table."""

    # Name of the database table associated with this model.
    __tablename__ = "users"

    # Unique primary key generated for each user.
    id: Mapped[int] = mapped_column(primary_key=True)

    # User's display name, limited to 100 characters.
    name: Mapped[str] = mapped_column(String(100))

    # Login email; it must be unique and is indexed for faster lookup.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Secure password hash. The original password is never stored.
    password_hash: Mapped[str] = mapped_column(String(255))
