from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.base import TimestampMixin


class User(TimestampMixin, db.Model):
    """User account model for authentication and identity."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # 1-to-1 relationship with UserProfile
    profile = db.relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # 1-to-many relationship with ResearchRecord
    research_records = db.relationship(
        "ResearchRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="desc(ResearchRecord.created_at)",
    )

    def __init__(self, email: str, **kwargs):
        super().__init__(**kwargs)
        self.email = email

    def set_password(self, password: str) -> None:
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifies the password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """Safe dictionary representation omitting sensitive credentials."""
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "profile": self.profile.to_dict() if self.profile else None,
        }


class UserProfile(TimestampMixin, db.Model):
    """User profile model containing investor preferences and focus."""

    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    display_name = db.Column(db.String(100), nullable=True)
    investment_focus = db.Column(db.String(255), nullable=True)
    risk_preference = db.Column(db.String(50), nullable=True)
    investment_horizon = db.Column(db.String(50), nullable=True)

    # Relationship back to User
    user = db.relationship("User", back_populates="profile")

    def __init__(self, user_id: int | None = None, display_name: str | None = None, **kwargs):
        super().__init__(**kwargs)
        if user_id is not None:
            self.user_id = user_id
        if display_name is not None:
            self.display_name = display_name

    def to_dict(self) -> dict:
        """Safe dictionary representation of user profile."""
        return {
            "display_name": self.display_name,
            "investment_focus": self.investment_focus,
            "risk_preference": self.risk_preference,
            "investment_horizon": self.investment_horizon,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
