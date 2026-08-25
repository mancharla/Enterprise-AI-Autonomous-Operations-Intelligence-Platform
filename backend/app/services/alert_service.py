from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.alert import Alert


class AlertService:

    @staticmethod
    def create_alert(
        db: Session,
        organization_id: int,
        facility_id: int,
        device_id: int,
        alert_type: str,
        severity: str,
        message: str,
        value: float | None = None,
        threshold: float | None = None,
    ) -> Alert:

        alert = Alert(
            organization_id=organization_id,
            facility_id=facility_id,
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            value=value,
            threshold=threshold,
            status="OPEN",
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def acknowledge_alert(
        db: Session,
        alert: Alert,
    ) -> Alert:

        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.utcnow()

        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def resolve_alert(
        db: Session,
        alert: Alert,
    ) -> Alert:

        alert.status = "RESOLVED"
        alert.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def get_summary(
        db: Session,
        organization_id: int,
    ) -> dict:

        total = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id
            )
            .count()
        )

        open_alerts = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id,
                Alert.status == "OPEN",
            )
            .count()
        )

        acknowledged = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id,
                Alert.status == "ACKNOWLEDGED",
            )
            .count()
        )

        resolved = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id,
                Alert.status == "RESOLVED",
            )
            .count()
        )

        critical = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id,
                Alert.severity == "CRITICAL",
                Alert.status != "RESOLVED",
            )
            .count()
        )

        high = (
            db.query(Alert)
            .filter(
                Alert.organization_id
                == organization_id,
                Alert.severity == "HIGH",
                Alert.status != "RESOLVED",
            )
            .count()
        )

        return {
            "total_alerts": total,
            "open_alerts": open_alerts,
            "acknowledged_alerts": acknowledged,
            "resolved_alerts": resolved,
            "critical_alerts": critical,
            "high_alerts": high,
        }