from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import UserCreate, ShowUser
from db.dals import UserDAL
from db.session import get_db

user_router = APIRouter()


# protected ф-ия. Для использ-я внутри другой ф-ии
async def _create_new_user(body: UserCreate, db: AsyncSession) -> ShowUser:
    async with db as session:  # орагнизуем сессию в рамках _create_new_user
        async with session.begin():
            user_dal = UserDAL(db_session=db)

            # создаем юзера в БД (sqlalchemy объект)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )

            # берем поля из sqlalchemy объекта и записываем в объект для ответа
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    return await _create_new_user(body, db=db)
