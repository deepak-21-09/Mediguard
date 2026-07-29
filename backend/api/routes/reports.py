from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user_id
from services.report_service import generate_health_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/health-report.pdf")
async def download_health_report(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate and download a PDF health report."""
    pdf_bytes = await generate_health_report(db, user_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=mediguard-report.pdf"},
    )
