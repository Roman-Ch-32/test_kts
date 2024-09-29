from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from schemas import ReservationAnswerSchema, ReservationAddProductSchema, ReservationGetSchema
from services import ReservationProductService, ReservationService

router = APIRouter()


@router.post("/reserve", response_model=ReservationAnswerSchema)
async def add_product_to_reserve(data: ReservationAddProductSchema = Body(),
                                 session: AsyncSession = Depends(get_async_session)) -> ReservationAnswerSchema:
    return await ReservationProductService(session=session).add_product(data=data)


@router.get("/reserve/{reservation_id}", response_model=ReservationGetSchema)
async def add_product_to_reserve(reservation_id: str,
                                 session: AsyncSession = Depends(get_async_session)) -> ReservationGetSchema:
    if ans := await ReservationService(session=session).find_one(pk=reservation_id):
        return ans
    raise HTTPException(status_code=404, detail="Reservation not found")


