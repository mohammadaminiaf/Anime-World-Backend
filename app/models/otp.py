from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timedelta
from app.db.database import Base


class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False)
    user_id = Column(String, nullable=False)
    otp_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    expires_at = Column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=5)
    )
    is_used = Column(Boolean, default=False)

    def to_dict(self):
        """
        Converts the OTP object to a dictionary.
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
