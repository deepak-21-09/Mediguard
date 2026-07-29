from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user_id
from memory.hindsight import get_memory
from services.symptom_service import list_symptoms, create_symptom
from api.schemas import SymptomCreate, SymptomOut

router = APIRouter(prefix="/symptoms", tags=["symptoms"])


@router.get("", response_model=list[SymptomOut])
async def get_symptoms(
    days: int = Query(90, ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await list_symptoms(db, user_id, days)


@router.post("", response_model=SymptomOut, status_code=201)
async def log_symptom(
    data: SymptomCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    memory = get_memory()
    return await create_symptom(db, user_id, data.model_dump(exclude_none=True), memory)
