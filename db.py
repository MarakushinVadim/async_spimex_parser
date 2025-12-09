import logging

from models import Base, SpimexTradingResultsBase


class DataBase:
    def __init__(self, engine):
        self.engine = engine

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def add_data(session, data):
        async with session() as session:
            async with session.begin():
                try:
                    obj_ = SpimexTradingResultsBase(
                        exchange_product_id=data.exchange_product_id,
                        exchange_product_name=data.exchange_product_name,
                        oil_id=data.oil_id,
                        delivery_basis_id=data.delivery_basis_id,
                        delivery_basis_name=data.delivery_basis_name,
                        delivery_type_id=data.delivery_type_id,
                        volume=data.volume,
                        total=data.total,
                        count=data.count,
                        date=data.date,
                        created_on=data.created_on,
                        updated_on=data.updated_on,
                    )
                    session.add(obj_)
                    session.commit()
                    session.refresh(obj_)
                    return obj_
                except Exception as e:
                    logging.warning(f"Ошибка при записи в БД - {e} - rollback")
                    session.rollback()
