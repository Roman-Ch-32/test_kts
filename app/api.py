import logging

from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from schemas import ReservationAnswerSchema, ReservationAddProductSchema, ReservationGetSchema, ProductAnswerSchema, \
    ProductAddSchema
from services import ReservationProductService, ReservationService, ProductService

router = APIRouter()


@router.post("/reserve",
             name="резервирование продукта",
             response_model=ReservationAnswerSchema)
async def add_product_to_reserve(data: ReservationAddProductSchema = Body(),
                                 session: AsyncSession = Depends(get_async_session)) -> ReservationAnswerSchema:
    logging.info(data)
    return await ReservationProductService(session=session).add_product(data=data)


@router.get("/reserve/{reservation_id}",
            name="проверка статуса резерва",
            response_model=ReservationGetSchema)
async def add_product_to_reserve(reservation_id: str,
                                 session: AsyncSession = Depends(get_async_session)) -> ReservationGetSchema:
    logging.info(f'Резерв {reservation_id} был запрошен')
    if ans := await ReservationService(session=session).find_one(pk=reservation_id):
        return ans
    logging.error(f'Резерв {reservation_id} был запрошен, ничего не нашлось')
    raise HTTPException(status_code=404, detail="Reservation not found")


@router.post('/product',
             name="добавление продуктов списком",
             response_model=ProductAnswerSchema)
async def add_products(data: ProductAddSchema = Body(...),
                       session: AsyncSession = Depends(get_async_session)) -> ProductAnswerSchema:
    logging.info(data)
    if ans := await ProductService(session=session).create_list(data=data):
        return ans
    logging.error(f'данные {data} не были загружены')
    raise HTTPException(status_code=404, detail="Reservation not found")
