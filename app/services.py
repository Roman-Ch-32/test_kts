from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import CRUDBase
from app.models import ReservationProduct, Reservation, Product
from app.schemas import (ReservationAnswerSchema, ReservationAddProductSchema, ModelFilter,
                         ReservationCreateSchema, ReservationFilter, ProductSchema)


@dataclass
class BaseService:
    session: AsyncSession | None = None


class ReservationService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели Reservation """

    async def find_one(self, pk: int | str) -> Reservation:
        result = CRUDBase(session=self.session, model=Reservation)
        pk = int(pk) if isinstance(pk, str) and pk.isdigit() else pk
        result.filter = ReservationFilter(reservation_id=pk)
        reserve = await result.get_one()
        return reserve

    async def create(self, data):
        result = CRUDBase(session=self.session, model=Reservation, data=data)
        reserve = await result.create()
        # await self.session.commit()
        return reserve


class ProductService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели Product """

    async def find_one(self, pk: int | str) -> Product:
        result = CRUDBase(session=self.session, model=Product)
        pk = int(pk) if isinstance(pk, str) and pk.isdigit() else pk
        result.filter = ModelFilter(id=pk)
        product = await result.get_one()
        return product

    async def update(self, data: ProductSchema) -> Product:
        result = CRUDBase(session=self.session, model=Product, data=data)
        product = await result.update()
        return product


class ReservationProductService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели ReservationProduct """

    async def add_product(self, data: ReservationAddProductSchema) -> ReservationAnswerSchema:
        result = CRUDBase(session=self.session, model=ReservationProduct)
        reservation = ReservationService(session=self.session)
        reserve = (await reservation.find_one(pk=data.reservation_id) or
                   await reservation.create(data=ReservationCreateSchema(reservation_id=data.reservation_id)))

        product = await ProductService(session=self.session).find_one(pk=data.product_id)
        if not product:
            return await self._bad_ans(reservation_id=data.reservation_id)

        result.data = data
        result.data.reservation_id = reserve.id
        result.data.product_id = product.id
        if product.quantity >= data.quantity:
            product.quantity = product.quantity - data.quantity
            try:
                await result.create()
                await ProductService(session=self.session).update(data=ProductSchema(**product.__dict__))
            except Exception as e:
                await self.session.rollback()
                return await self._bad_ans(reservation_id=data.reservation_id)

        await self.session.commit()
        return await self._good_ans(reservation_id=data.reservation_id)

    @staticmethod
    async def _good_ans(reservation_id) -> ReservationAnswerSchema:
        """ удачный ответ от бд """
        return ReservationAnswerSchema(status='success',
                                       message='Reservation completed successfully.',
                                       reservation_id=f'{reservation_id}')

    @staticmethod
    async def _bad_ans(reservation_id) -> ReservationAnswerSchema:
        """ неудачный ответ от бд """
        return ReservationAnswerSchema(status='error',
                                       message='Not enough stock available.',
                                       reservation_id=f'{reservation_id}')
