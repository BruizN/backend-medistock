from app.core.auditmixin import AuditMixin

# You can add other global mixins here or just expose the AuditMixin for models
# We can also create a Base model if needed, but SQLModel already provides this.
# For now, models will inherit from SQLModel, table=True and optionally AuditMixin.

class BaseTable(AuditMixin):
    pass
