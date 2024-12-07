from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ClientApp



class ClientAppDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_app_by_name(self, app_name: str):
        query = select(ClientApp).where(ClientApp.app_name == app_name)
        res = await self.db_session.execute(query)
        app = res.fetchone()
        if app is not None:
            return app[0]

    async def get_app_by_hashed_key(self, hashed_key: str):
        query = select(ClientApp).where(ClientApp.hashed_key == hashed_key)
        res = await self.db_session.execute(query)
        app = res.fetchone()
        if app is not None:
            return app[0]

    async def get_apps(self):
        query = select(ClientApp)
        res = await self.db_session.execute(query)
        client_apps = res.scalars().all()
        return client_apps
