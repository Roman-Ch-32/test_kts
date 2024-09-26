from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.schemas import ReservationAnswerSchema, ReservationAddProductSchema
from app.services import ReservationProductService

router = APIRouter()


@router.post("/reserve", response_model=ReservationAnswerSchema)
async def add_product_to_reserve(data: ReservationAddProductSchema = Body(),
                                 session: AsyncSession = Depends(get_async_session)):
    return await ReservationProductService(session=session).add_product(data=data)
