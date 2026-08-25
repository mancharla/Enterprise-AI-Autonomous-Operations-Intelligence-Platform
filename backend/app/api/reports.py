import csv
import io
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.core.dependencies import (
    get_current_user,
    get_database,
)

from app.models.user import User

from app.schemas.reports import (
    ReportResponse,
)

from app.services.report_service import (
    ReportService,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def get_report(
    db: Session,
    current_user: User,
    device_id: int,
):
    service = ReportService()

    try:
        return service.generate_device_report(
            db=db,
            organization_id=current_user.organization_id,
            device_id=device_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/device/{device_id}",
    response_model=ReportResponse,
)
def generate_device_report(
    device_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):
    return get_report(
        db=db,
        current_user=current_user,
        device_id=device_id,
    )


@router.get(
    "/device/{device_id}/csv",
)
def export_device_report_csv(
    device_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):

    report = get_report(
        db=db,
        current_user=current_user,
        device_id=device_id,
    )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "Metric",
            "Value",
        ]
    )

    writer.writerow(
        [
            "Device ID",
            report["device_id"],
        ]
    )

    writer.writerow(
        [
            "Generated At",
            report["generated_at"],
        ]
    )

    writer.writerow(
        [
            "Overall Risk",
            report["overall_risk"],
        ]
    )

    writer.writerow(
        [
            "Current Energy (kWh)",
            report["current_energy_kwh"],
        ]
    )

    writer.writerow(
        [
            "Average Energy (kWh)",
            report["average_energy_kwh"],
        ]
    )

    writer.writerow(
        [
            "Peak Energy (kWh)",
            report["peak_energy_kwh"],
        ]
    )

    writer.writerow(
        [
            "Minimum Energy (kWh)",
            report["minimum_energy_kwh"],
        ]
    )

    writer.writerow(
        [
            "Utilization (%)",
            report["utilization_percent"],
        ]
    )

    writer.writerow(
        [
            "Temperature (C)",
            report["temperature_c"],
        ]
    )

    writer.writerow(
        [
            "Forecast Model",
            report["forecast"]["model"],
        ]
    )

    writer.writerow(
        [
            "Forecast Horizon (hours)",
            report["forecast"]["horizon_hours"],
        ]
    )

    writer.writerow(
        [
            "Average Predicted Energy (kWh)",
            report["forecast"][
                "average_predicted_energy_kwh"
            ],
        ]
    )

    writer.writerow(
        [
            "Peak Predicted Energy (kWh)",
            report["forecast"][
                "peak_predicted_energy_kwh"
            ],
        ]
    )

    writer.writerow(
        [
            "Forecast Increase (%)",
            report["forecast"][
                "forecast_increase_percent"
            ],
        ]
    )

    writer.writerow(
        [
            "Peak Forecast Time",
            report["forecast"]["peak_time"],
        ]
    )

    writer.writerow(
        [
            "Total Records",
            report["anomalies"]["total_records"],
        ]
    )

    writer.writerow(
        [
            "Anomaly Count",
            report["anomalies"]["anomaly_count"],
        ]
    )

    writer.writerow(
        [
            "Anomaly Rate (%)",
            report["anomalies"][
                "anomaly_rate_percent"
            ],
        ]
    )

    writer.writerow(
        [
            "Primary Root Cause",
            report["root_cause"].get(
                "primary_factor",
                "",
            ),
        ]
    )

    writer.writerow(
        [
            "Root Cause Confidence",
            report["root_cause"].get(
                "confidence",
                "",
            ),
        ]
    )

    writer.writerow(
        [
            "Optimization Strategy",
            report["optimization"].get(
                "recommended_strategy",
                "",
            ),
        ]
    )

    writer.writerow(
        [
            "Estimated Savings (%)",
            report["estimated_savings_percent"],
        ]
    )

    writer.writerow(
        [
            "Estimated Energy Savings (kWh)",
            report[
                "estimated_energy_savings_kwh"
            ],
        ]
    )

    writer.writerow(
        [
            "Recommendation",
            report["recommendation"].get(
                "recommendation",
                "",
            ),
        ]
    )

    writer.writerow(
        [
            "Executive Summary",
            report["executive_summary"],
        ]
    )

    output.seek(0)

    filename = (
        f"device_{device_id}_report.csv"
    )

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )


@router.get(
    "/device/{device_id}/pdf",
)
def export_device_report_pdf(
    device_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(
        get_database
    ),
):

    report = get_report(
        db=db,
        current_user=current_user,
        device_id=device_id,
    )

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    elements = []

    elements.append(
        Paragraph(
            "Enterprise AI Operations",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            f"Device {device_id} Operational Intelligence Report",
            heading_style,
        )
    )

    elements.append(
        Spacer(1, 8)
    )

    elements.append(
        Paragraph(
            f"Generated at: "
            f"{report['generated_at']}",
            body_style,
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    elements.append(
        Paragraph(
            "Executive Summary",
            heading_style,
        )
    )

    elements.append(
        Paragraph(
            report["executive_summary"],
            body_style,
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------
    # Current Metrics
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Current Operational Metrics",
            heading_style,
        )
    )

    metrics = [
        [
            "Metric",
            "Value",
        ],
        [
            "Current Energy",
            f"{report['current_energy_kwh']} kWh",
        ],
        [
            "Average Energy",
            f"{report['average_energy_kwh']} kWh",
        ],
        [
            "Peak Energy",
            f"{report['peak_energy_kwh']} kWh",
        ],
        [
            "Minimum Energy",
            f"{report['minimum_energy_kwh']} kWh",
        ],
        [
            "Utilization",
            f"{report['utilization_percent']}%",
        ],
        [
            "Temperature",
            f"{report['temperature_c']} °C",
        ],
        [
            "Overall Risk",
            report["overall_risk"],
        ],
    ]

    table = Table(
        metrics,
        colWidths=[
            80 * mm,
            80 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(table)

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------
    # Forecast
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Forecast",
            heading_style,
        )
    )

    forecast_data = [
        [
            "Metric",
            "Value",
        ],
        [
            "Model",
            report["forecast"]["model"],
        ],
        [
            "Horizon",
            f"{report['forecast']['horizon_hours']} hours",
        ],
        [
            "Average Prediction",
            f"{report['forecast']['average_predicted_energy_kwh']} kWh",
        ],
        [
            "Peak Prediction",
            f"{report['forecast']['peak_predicted_energy_kwh']} kWh",
        ],
        [
            "Forecast Increase",
            f"{report['forecast']['forecast_increase_percent']}%",
        ],
        [
            "Peak Time",
            str(report["forecast"]["peak_time"]),
        ],
    ]

    forecast_table = Table(
        forecast_data,
        colWidths=[
            80 * mm,
            80 * mm,
        ],
    )

    forecast_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(
        forecast_table
    )

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------
    # Anomalies
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Anomaly Analysis",
            heading_style,
        )
    )

    anomaly_data = [
        [
            "Metric",
            "Value",
        ],
        [
            "Total Records",
            report["anomalies"]["total_records"],
        ],
        [
            "Anomaly Count",
            report["anomalies"]["anomaly_count"],
        ],
        [
            "Anomaly Rate",
            f"{report['anomalies']['anomaly_rate_percent']}%",
        ],
    ]

    anomaly_table = Table(
        anomaly_data,
        colWidths=[
            80 * mm,
            80 * mm,
        ],
    )

    anomaly_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(
        anomaly_table
    )

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------
    # Root Cause
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Root Cause Analysis",
            heading_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Primary Factor:</b> "
            f"{report['root_cause'].get('primary_factor', 'Unknown')}",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Confidence:</b> "
            f"{report['root_cause'].get('confidence', 0)}",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            report["root_cause"].get(
                "root_cause",
                "",
            ),
            body_style,
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    # -----------------------------------------
    # Optimization
    # -----------------------------------------

    elements.append(
        Paragraph(
            "Optimization Recommendation",
            heading_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Strategy:</b> "
            f"{report['optimization'].get('recommended_strategy', '')}",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Expected Savings:</b> "
            f"{report['estimated_savings_percent']}%",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Expected Energy Savings:</b> "
            f"{report['estimated_energy_savings_kwh']} kWh",
            body_style,
        )
    )

    elements.append(
        Paragraph(
            report["recommendation"].get(
                "recommendation",
                "",
            ),
            body_style,
        )
    )

    document.build(elements)

    buffer.seek(0)

    filename = (
        f"device_{device_id}_report.pdf"
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )