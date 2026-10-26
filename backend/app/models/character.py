from datetime import datetime, timezone
from app.extensions import db


class Character(db.Model):
    __tablename__ = "characters"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

    character_class = db.Column(
        db.String(30),
        nullable=False
    )

    level = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    experience = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="characters"
    )
