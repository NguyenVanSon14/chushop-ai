from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.modules.analytics.schema import AnalyticsRead
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/businesses/{business_id}/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsRead)
def get_analytics(
    business_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
    date_from: Annotated[date, Query()],
    date_to: Annotated[date, Query()],
) -> AnalyticsRead:
    return AnalyticsService(db).get(
        business_id=business_id,
        date_from=date_from,
        date_to=date_to,
        user=current_user,
    )
