# ====================================================================================================
# HDM AI Engine — /v1/image
# ====================================================================================================

from fastapi import APIRouter
from schemas.image import ImageRequest
from services.image_service import image_service

router = APIRouter(prefix="/v1", tags=["Image"])


@router.post("/image")
async def image(request: ImageRequest):
    uid = request.user_id or "anon"

    if request.mode == "analyze" and request.image_base64:
        result = await image_service.analyze(uid, request.image_base64, request.prompt)
    elif request.mode == "variations" and request.image_base64:
        result = await image_service.variations(uid, request.image_base64)
    else:
        result = await image_service.generate(
            uid, request.prompt,
            style=request.style,
            size=request.size,
            num_images=request.num_images,
        )
    return {"success": True, "data": result}