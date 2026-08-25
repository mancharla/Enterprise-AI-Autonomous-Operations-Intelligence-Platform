from app.core.database import engine, Base

# Import all models so SQLAlchemy registers them.
from app.models import (
    Organization,
    User,
    Facility,
    Device,
    Dataset,
    OperationalRecord,
    ForecastAccuracy,
    MLModel,
    Alert,
    AutonomousAction,
)


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")