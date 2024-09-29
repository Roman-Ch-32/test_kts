from dataclasses import dataclass

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from crud import CRUDBase
from models import ReservationProduct, Reservation, Product
from schemas import (ReservationAnswerSchema, ReservationAddProductSchema, ModelFilter,
                     ReservationCreateSchema, ReservationFilter, ProductSchema,
                     ReservationProductUpdateSchema, ReservationProductCreateSchema, ReservationGetSchema,
                     ProductAnswerSchema, ProductAddSchema)


@dataclass
class BaseService:
    session: AsyncSession | None = None


class ReservationService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели Reservation """

    async def find_one(self, pk: str) -> ReservationGetSchema | None:
        result = CRUDBase(session=self.session, model=Reservation)
        result.filter = ReservationFilter(reservation_id=pk)
        reserve = await result.get_one()
        return reserve

    async def create(self, data):
        result = CRUDBase(session=self.session, model=Reservation, data=data)
        result.data.status = 'new'
        reserve = await result.create()
        await self.session.commit()
        await self.session.refresh(reserve)
        return reserve


class ProductService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели Product """

    async def find_one(self, pk: int | str) -> Product | None:
        result = CRUDBase(session=self.session, model=Product)
        pk = int(pk) if isinstance(pk, str) and pk.isdigit() else pk if isinstance(pk, int) else None
        if not pk:
            return None
        result.filter = ModelFilter(id=pk)
        product = await result.get_one()
        return product

    async def create_list(self, data) -> ProductAnswerSchema:
        result = CRUDBase(session=self.session, model=Product, list_data=data.products)
        products = await result.create_list()
        print(products, type(products))
        if products:
            await self.session.commit()
            return ProductAnswerSchema(status='success',
                                       message=f'{len(products)} products created from {len(data.products)}')
        await self.session.rollback()
        return ProductAnswerSchema(status='error',
                                   message=f'{products} products created from {len(data.products)}')

    async def update(self, data: ProductSchema) -> Product:
        result = CRUDBase(session=self.session, model=Product, data=data)
        product = await result.update()
        return product


class ReservationProductService(BaseService):
    """ Сервис для работы с данными и бизнес-логики для модели ReservationProduct """

    async def add_product(self, data: ReservationAddProductSchema) -> ReservationAnswerSchema:
        data.timestamp = data.timestamp.replace(tzinfo=None)
        result = CRUDBase(session=self.session, model=ReservationProduct)
        """ проверяем существование продукта и его доступность, вычитаем резерв """
        product = await ProductService(session=self.session).find_one(pk=data.product_id)
        if not product or product.quantity < data.quantity:
            return await self._bad_ans(reservation_id=data.reservation_id)
        product.quantity -= data.quantity
        """ проверяем существует ли такой резерв на нашем складе,
            если нет, то создаём
        """
        reservation = ReservationService(session=self.session)
        reservation = (await reservation.find_one(pk=data.reservation_id) or
                       await reservation.create(data=ReservationCreateSchema(reservation_id=data.reservation_id)))
        """ проверяем, если ли уже такой товар в таком резерве,
            если есть, то обновлем количество товара в резерве,
            возвращаем результат
        """
        reservation_product = None
        for item in reservation.reserve_products if reservation.reserve_products else []:
            if item.product_id == product.id:
                reservation_product = item
        if reservation_product:
            result.data = ReservationProductUpdateSchema(**reservation_product.__dict__)
            result.data.quantity += data.quantity
            try:
                """ Производим транзакцию, добавляем резерв и меняем доступное количество товаров """
                await result.update()
                await ProductService(session=self.session).update(data=ProductSchema(**product.__dict__))
                await self.session.commit()
            except SQLAlchemyError as e:
                print(e)
                await self.session.rollback()
                return await self._bad_ans(reservation_id=data.reservation_id)
            return await self._good_ans(reservation_id=data.reservation_id)
        """ если такого товара в таком резерве нет,
            то создаём новую запись о том, что мы добавили товар в этот резерв.
            т.к. в теории этим же сервисом мы можем и уменьшать количество товара в резерве,
             послав отрицательное значение, проверяем тут добавляемое количество товара на отрицательное значение
        """
        if data.quantity < 0:
            return await self._bad_ans(reservation_id=data.reservation_id)
        result.data = ReservationProductCreateSchema(reservation_id=reservation.id,
                                                     product_id=product.id,
                                                     quantity=data.quantity,
                                                     timestamp=data.timestamp)
        try:
            """ Производим транзакцию, добавляем резерв и меняем доступное количество товаров """
            await result.create()
            await ProductService(session=self.session).update(data=ProductSchema(**product.__dict__))
            await self.session.commit()
        except SQLAlchemyError as e:
            print(e)
            await self.session.rollback()
            return await self._bad_ans(reservation_id=data.reservation_id)
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
