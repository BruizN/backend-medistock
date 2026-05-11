from sqlmodel import Field
from app.core.auditmixin import AuditMixin

class User(AuditMixin, table=True):
    __tablename__ = "users"
    
    email: str = Field(index=True, unique=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    role: str = Field(default="client", max_length=50)
