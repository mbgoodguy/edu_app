# -- ITERACTION WITH DB IN BUSINESS CONTEXT --
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserDAL:
    """
    Слой для доступа к данным юзера. Т.е класс, отвечающий за все бизнесовые взаимод-я в рамках
    работы с юзерами - за CRUD и т.д. Он будет инкапсулировать в себе определ-ую бизнес-логику, которая будет вынесена
    в дальнейшем на урвоень обработчиков(handler'ов)
    """

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, name: str, surname: str, email: str) -> User:
        new_user = User(name=name, surname=surname, email=email)
        self.db_session.add(new_user)
        await self.db_session.flush()  # не коммитим в БД, просто отправка в БД без сохранения
        return new_user
