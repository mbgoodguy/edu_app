# -- API MODELS (pydantic) --
# паттерн вынесен в global scope чтобы не пересоздавать его в ф-ях, что затратно по памяти. Лучше создать 1 раз
import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from starlette import status

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
