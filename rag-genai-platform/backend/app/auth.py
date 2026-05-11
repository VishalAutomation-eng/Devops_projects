"""Authentication domain service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import UserCreate, UserLogin
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    """Service responsible for user registration and login."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize service with a database session."""

        self.db = db

    async def register(self, payload: UserCreate) -> User:
        """Create a user with a unique email.

        :raises ValueError: If the email already exists.
        """

        existing = await self.db.scalar(select(User).where(User.email == payload.email))
        if existing:
            raise ValueError("Email already registered")
        user = User(email=payload.email, hashed_password=hash_password(payload.password))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def login(self, payload: UserLogin) -> str:
        """Authenticate user and return an access token.

        :raises ValueError: If credentials are invalid.
        """

        user = await self.db.scalar(select(User).where(User.email == payload.email))
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return create_access_token(str(user.id))
