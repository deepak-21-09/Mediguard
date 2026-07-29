from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user_id
from memory.hindsight import get_memory
from services.medication_service import (
    list_medications,
    get_medication,
    create_medication,
    update_medication,
    delete_medication,
)
from services.ocr_service import extract_prescription
from api.schemas import MedicationCreate, MedicationUpdate, MedicationOut, InteractionOut

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("", response_model=list[MedicationOut])
async def get_medications(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await list_medications(db, user_id)


@router.get("/{med_id}", response_model=MedicationOut)
async def get_medication_by_id(
    med_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    med = await get_medication(db, user_id, med_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.post("", response_model=dict, status_code=201)
async def add_medication(
    data: MedicationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    memory = get_memory()
    med, interactions = await create_medication(db, user_id, data.model_dump(), memory)
    return {
        "medication": MedicationOut.model_validate(med),
        "interactions": [InteractionOut.model_validate(i) for i in interactions],
        "interaction_count": len(interactions),
        "has_critical": any(i.severity.value == "critical" for i in interactions),
    }


@router.put("/{med_id}", response_model=MedicationOut)
async def edit_medication(
    med_id: str,
    data: MedicationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    med = await update_medication(db, user_id, med_id, data.model_dump(exclude_none=True))
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.delete("/{med_id}", status_code=204)
async def remove_medication(
    med_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_medication(db, user_id, med_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medication not found")


@router.post("/scan-prescription", response_model=dict)
async def scan_prescription(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
):
    """
    Upload a prescription image.
    - Saves to Supabase Storage (or local /tmp fallback)
    - Extracts medication data via GPT-4o Vision
    - Returns structured medication list + storage URL
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()

    # Save to storage
    from services.storage_service import save_prescription_image
    storage_url = await save_prescription_image(user_id, image_bytes, file.content_type)

    # Extract medication data
    result = await extract_prescription(image_bytes)
    result["prescription_image_url"] = storage_url
    return result
