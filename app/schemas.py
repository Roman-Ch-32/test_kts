from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReservationAddProductSchema(BaseModel):
    reservation_id: str
    product_id: str
    quantity: int
    timestamp: datetime


class ProductSchema(BaseModel):
    id: str
    name: str
    quantity: int


class ReservationCreateSchema(BaseModel):
    reservation_id: str
    products: list[ProductSchema] | None = None
    status: str | None = None


class ReservationGetSchema(ReservationCreateSchema):
    id: int | None = None


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


class DateFilter(BaseModel):
    created_at: Optional[tuple[datetime.date, datetime.date]] | None = None


class BaseSetId(BaseModel):
    id: list[int] | None = None
