import re
import uuid

import uvicorn
from fastapi import HTTPException, FastAPI, APIRouter
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import Column, UUID, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette import status

import settings

# -- APP INSTANCE --
app = FastAPI(title="edu_platform")

# -- ITERACTION WITH DB --
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# -- DB MODELS --
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)


# -- ITERACTION WITH DB IN BUSINESS CONTEXT --
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


# -- API MODELS (pydantic) --
# паттерн вынесен в global scope чтобы не пересоздавать его в ф-ях, что затратно по памяти. Лучше создать 1 раз
LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """Говорим pydantic конвертировать все non dict объекты, которые в него входят, в json через orm_mode"""

        from_attributes = True


class ShowUser(
    TunedModel
):  # класс для ответа. Выдает данные в json формате, т.к наследуется от TunedModel
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(
    BaseModel
):  # класс обработки входящего запроса. В json преобразовывать не требуется
    name: str
    surname: str
    email: EmailStr

    @field_validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Name should contains only letters",
            )
        return value

    @field_validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Surname should contains only letters",
            )
        return value


# -- API ROUTES (endpoints) --
user_router = APIRouter()


# protected ф-ия. Для использ-я внутри другой ф-ии
async def _create_new_user(body: UserCreate) -> ShowUser:
    async with async_session() as session:  # орагнизуем сессию в рамках _create_new_user
        async with session.begin():
            user_dal = UserDAL(session)

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
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)


main_api_router = APIRouter()
main_api_router.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
