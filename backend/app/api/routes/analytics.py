from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import require_permission
from app.schemas import ExecutiveMetricsResponse, WeeklyReportResponse
from app.services.analytics import analytics_service

router = APIRouter()


@router.get("/executive", response_model=ExecutiveMetricsResponse)
async def get_executive_metrics(
    _: Annotated[object, Depends(require_permission("view_dashboards"))],
):
    data = analytics_service.get_executive_metrics()
    return ExecutiveMetricsResponse(
        metrics={
            k: v for k, v in data.items()
            if k not in ("department_performance", "retention_trends")
        },
        department_performance=data["department_performance"],
        retention_trends=data["retention_trends"],
    )


@router.get("/weekly-report", response_model=WeeklyReportResponse)
async def get_weekly_report(
    _: Annotated[object, Depends(require_permission("view_dashboards"))],
):
    report = analytics_service.generate_weekly_report()
    return WeeklyReportResponse(
        title=report["title"],
        period=report["period"],
        summary=report["summary"],
        highlights=report["highlights"],
        recommendations=report["recommendations"],
    )
