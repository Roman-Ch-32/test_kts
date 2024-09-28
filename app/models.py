import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ReservationProduct(Base):
    __tablename__ = 'reservation_product'
    """ промежуточная таблица для связи продуктов и резерва """
    reservation_id: Mapped[int] = mapped_column(ForeignKey('reservation.id'), primary_key=True)
    reservation: Mapped['Reservation'] = relationship('Reservation', back_populates='reserve_products')
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'), primary_key=True)
    product: Mapped['Product'] = relationship('Product', lazy='joined')
    quantity: Mapped[int] = mapped_column(nullable=False, comment='Количество товаров в резерве')
    timestamp: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())


class Reservation(Base):
    __tablename__ = 'reservation'
    """ Возможно это что-то в виде корзины и тут может быть много товаров разных
        Судя по описанию в ТЗ сами резервы создаются не в нашем сервисе,
        мы только получаем их идентификатор
    """
    reservation_id: Mapped[str] = mapped_column(nullable=False)
    reserve_products: Mapped[list['ReservationProduct']] = relationship('ReservationProduct',
                                                                        lazy='joined')
    status: Mapped['str'] = mapped_column(nullable=False, comment='статус', default='new')


class Product(Base):
    __tablename__ = 'product'
    """ Продукт """
    name: Mapped[str] = mapped_column(nullable=False, comment='название продукта')
    quantity: Mapped[int] = mapped_column(nullable=False, default=0, comment='количество продукта,'
                                                                             ' доступное для покупки или резерва')
    reservations: Mapped[list['Reservation']] = relationship('Reservation',
                                                             secondary='reservation_product', lazy='select')
