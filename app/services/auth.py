from datetime import datetime, timedelta, timezone
from typing import Annotated, Union, Optional

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.session import Session
from passlib.context import CryptContext

import settings
from db.models import ClientApp
from db.dals import ClientAppDAL
from db.session import get_db


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_api_key(api_key:str) -> str:
    return PWD_CONTEXT.hash(api_key)


def verify_api_key(api_key:str, hashed_key:str) -> bool:
    return PWD_CONTEXT.verify(api_key, hashed_key)


async def authenticate(
        api_key: str = Header(...,alias="api-key"),
        db: AsyncSession = Depends(get_db)
) -> Optional[ClientApp]:
    client_dal = ClientAppDAL(db_session=db)
    client_apps = await client_dal.get_apps()
    for client_app in client_apps:
        if verify_api_key(api_key, client_app.hashed_key):
            return client_app
    raise HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
