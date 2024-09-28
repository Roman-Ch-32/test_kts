from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReservationAddProductSchema(BaseModel):
    """ схема для апи для добавления товара в резерв """
    reservation_id: str
    product_id: str
    quantity: int
    timestamp: datetime


class ReservationProductGetSchema(BaseModel):
    """ схема показа резерва продукта """
    product: 'ProductSchema'
    quantity: int
    timestamp: datetime


class ReservationProductCreateSchema(BaseModel):
    """ схема для добавления записи о резерве в бд """
    reservation_id: int
    product_id: int
    quantity: int
    timestamp: datetime


class ReservationProductUpdateSchema(ReservationProductCreateSchema):
    """ схема для обновления записи о продукте в резерве """
    id: int


class ProductSchema(BaseModel):
    """ схема продукта """
    id: str
    name: str
    quantity: int


class ReservationCreateSchema(BaseModel):
    reservation_id: str
    status: str | None = None


class ReservationGetSchema(ReservationCreateSchema):
    reserve_products: list[ReservationProductGetSchema]


class ReservationAnswerSchema(BaseModel):
    status: str
    message: str
    reservation_id: str


class ModelFilter(BaseModel):
    id: int | None = None
    page: int | None = None
    limit: int | None = None


class ReservationFilter(ModelFilter):
    reservation_id: str


class ReservationProductFilter(ModelFilter):
    reservation: str


class DateFilter(BaseModel):
    created_at: Optional[tuple[datetime.date, datetime.date]] | None = None


class BaseSetId(BaseModel):
    id: list[int] | None = None
