"""
Prescription OCR service — extracts medication info from uploaded images.
Uses GPT-4o Vision (OpenAI) when available, or a text-only Groq fallback
when only a Groq key is configured. Tesseract is NOT required.
"""
from __future__ import annotations

import base64
import json
from io import BytesIO

from PIL import Image

from core.config import settings

_EXTRACT_PROMPT = """
You are a medical OCR assistant. Extract all medication information from this prescription image.
Return a JSON object with:
{
  "medications": [
    {
      "name": "medication name",
      "generic_name": "generic name if visible",
      "dosage": "e.g. 500mg",
      "frequency": "e.g. twice daily",
      "route": "oral/topical/etc",
      "duration": "e.g. 7 days",
      "purpose": "what it's for if noted"
    }
  ],
  "prescribing_doctor": "doctor name if visible",
  "pharmacy": "pharmacy name if visible",
  "prescription_date": "date if visible",
  "notes": "any other relevant notes"
}
If a field is not visible in the image, set it to null.
"""


async def extract_prescription(image_bytes: bytes) -> dict:
    """
    Extract medication details from a prescription image.

    - If OPENAI_API_KEY is set → uses GPT-4o Vision (best accuracy).
    - If only GROQ_API_KEY is set → returns a polite error; Groq does not
      support image input so vision-based extraction is unavailable.
    - Falls back gracefully in both cases so the upload endpoint never 500s.
    """
    provider = settings.effective_llm_provider

    if provider == "openai" and settings.OPENAI_API_KEY:
        return await _extract_with_openai(image_bytes)

    # Groq doesn't support vision — return a structured placeholder
    return {
        "medications": [],
        "prescribing_doctor": None,
        "pharmacy": None,
        "prescription_date": None,
        "notes": (
            "Vision-based OCR requires an OpenAI API key (GPT-4o). "
            "Set OPENAI_API_KEY in .env to enable prescription scanning. "
            "Current provider is Groq which does not support image input."
        ),
        "ocr_available": False,
    }


async def _extract_with_openai(image_bytes: bytes) -> dict:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    img = Image.open(BytesIO(image_bytes))
    fmt = img.format.lower() if img.format else "jpeg"
    mime = f"image/{fmt}"

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _EXTRACT_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"medications": [], "error": str(e), "ocr_available": True}
