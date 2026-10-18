from datetime import datetime, timezone
from app.extensions import db


class SaveGame(db.Model):
    __tablename__ = "save_games"

    id = db.Column(db.Integer, primary_key=True)

    character_id = db.Column(
        db.Integer,
        db.ForeignKey("characters.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    world_id = db.Column(
        db.String(100),
        nullable=False,
        default="",
    )

    checkpoint_id = db.Column(
        db.String(100),
        nullable=False,
        default="",
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="in_progress",
    )

    progress_data = db.Column(
        db.JSON,
        nullable=False,
        default=dict,
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "character_id": self.character_id,
            "world_id": self.world_id,
            "checkpoint_id": self.checkpoint_id,
            "status": self.status,
            "progress_data": self.progress_data,
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }
