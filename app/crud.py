import dataclasses
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Base
from schemas import ModelFilter, DateFilter, BaseSetId


@dataclasses.dataclass
class CrudInit:
    set_id: BaseSetId | None = None
    session: AsyncSession | None = None
    filter: ModelFilter | None = None
    filter_to_many: ModelFilter | None = None
    model: Base | Any | None = None
    data: dict | BaseModel | Base | None = None
    list_data: list[dict] | list[BaseModel] | None = None
    model_to_many: Base | Any | None = None
    data_to_many: dict | BaseModel | None = None
    date_filter: DateFilter | None = None


class CRUDBase(CrudInit):

    async def create(self) -> Base:
        data = self.data if isinstance(self.data, dict) else self.data.dict()
        data.pop('id') if data.get('id') is None and 'id' in data else None
        sql = insert(self.model).values(**data).returning(self.model)
        result = (await self.session.execute(sql)).scalars().unique().one_or_none()
        return result


    async def create_list(self) -> list[Base]:
        ans = []
        for data in self.list_data:
            self.data = data
            ans.append(await self.create())
        return ans

    async def create_to_many(self) -> Base:
        data = self.data_to_many if isinstance(self.data_to_many, dict) else self.data_to_many.dict()
        data.pop('id') if data.get('id') is None else None
        sql = insert(self.model_to_many).values(**data).returning(self.model_to_many)
        result = (await self.session.execute(sql)).scalars().unique().one_or_none()
        return result

    async def update(self):
        sql = update(self.model).where(self.model.id == self.data.id).values(**self.data.dict()).returning(self.model)
        result = (await self.session.execute(sql)).scalars().unique().one_or_none()
        return result

    async def get_order_count(self, is_archive: bool) -> int:
        """ Возможно этот роут нужен для пагинации? сомнительно. """
        sql = select(func.count()).select_from(self.model).where(self.model.is_archive == is_archive)
        return await self.session.scalar(sql)

    async def get_one(self):
        sql = (select(self.model).limit(self.filter.limit if 'limit' in self.filter else None)
               .offset(self.filter.page if 'page' in self.filter else None).where(*self._filter()))
        result = (await self.session.execute(sql)).scalars().unique().one_or_none()
        return result

    async def get_one_to_many(self) -> Base:
        sql = (select(self.model_to_many).limit(self.filter_to_many.limit if 'limit' in self.filter_to_many else None)
               .offset(self.filter_to_many.page if 'page' in self.filter_to_many else None).
               where(*self._filter_to_many()))
        result = (await self.session.execute(sql)).scalars().unique().first()
        return result

    async def get_all(self) -> list[Base]:
        sql = (select(self.model).limit(self.filter.limit if 'limit' in self.filter else None)
               .offset(self.filter.page if 'page' in self.filter else None).
               where(*self._filter(),
               *self._and_date_filter()))
        result = (await self.session.execute(sql)).scalars().unique().all()
        return result

    async def get_all_like(self) -> list[Base]:
        sql = (select(self.model).limit(self.filter.limit if 'limit' in self.filter else None)
               .offset(self.filter.page if 'page' in self.filter else None)
               .where(*self._filter_like(), *self._and_date_filter()))
        result = (await self.session.execute(sql)).scalars().unique().all()
        return result

    async def get_all_to_many(self) -> list[Base]:
        sql = (select(self.model_to_many).limit(self.filter_to_many.limit).
               offset(self.filter_to_many.page).where(*self._filter_to_many()))
        result = (await self.session.execute(sql)).scalars().unique().all()
        return result

    def _filter(self):
        model_filter = [getattr(self.model, field) == value
                        for field, value in self.filter.dict().items() if
                        field in self.model.__dict__ and value is not None] if self.filter else []
        return model_filter

    def _and_date_filter(self):
        model_filter = [getattr(self.model, field).between(value)
                        for field, value in self.date_filter.dict().items() if
                        field in self.model.__dict__ and value is not None] if self.date_filter else []
        return model_filter

    def _filter_like(self):
        model_filter = [getattr(self.model, field).ilike(f"%{value}%")
                        for field, value in self.filter.dict().items() if
                        field in self.model.__dict__ and value is not None] if self.filter else []
        return model_filter

    def _filter_to_many(self):
        model_filter = [getattr(self.model_to_many, field) == value for field, value in
                        self.filter_to_many.dict().items() if field in
                        self.model_to_many.__dict__ and value is not None] if self.filter_to_many else []
        return model_filter

    def _filter_in(self):
        model_filter = [getattr(self.model, field).in_(value) for field, value in
                        self.set_id.dict().items() if field in
                        self.model.__dict__ and value is not None]
        return model_filter

    async def get_all_in(self) -> list[Base]:
        sql = select(self.model).filter(*self._filter_in())
        db_query = (await self.session.execute(sql)).scalars().unique().all()
        return db_query

    async def delete_forever(self):
        sql = delete(self.model).filter(*self._filter())
        result = await self.session.execute(sql)
        return result