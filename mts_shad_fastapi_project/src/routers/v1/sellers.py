from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
#from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller

sellers_router = APIRouter(tags=["Sellers"], prefix="/Sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для регистрации продавца в системе.
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_Seller(
    Seller: IncomingSeller, session: DBSession
):  # прописываем модель валидирующую входные данные и сессию как зависимость.
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_Seller = Seller(
        first_name=Seller.first_name,
        last_name=Seller.last_name,
        email=Seller.email,
        password=Seller.password,
        books_for_sale = Seller.books_for_sale
    )
    session.add(new_Seller)
    await session.flush()

    return new_Seller


# Ручка для получения списка всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_Sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    Sellers = res.scalars().all()
    return {"Sellers": Sellers}


# Ручка для получения книги по ее ИД
@sellers_router.get("/{Seller_id}", response_model=ReturnedSeller)
async def get_Seller(Seller_id: int, session: DBSession):
    res = await session.get(Seller, Seller_id)
    return res


# Ручка для удаления книги
@sellers_router.delete("/{Seller_id}")
async def delete_Seller(Seller_id: int, session: DBSession):
    deleted_Seller = await session.get(Seller, Seller_id)
    print(deleted_Seller)  
    if deleted_Seller:
        await session.delete(deleted_Seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  # Response может вернуть текст и метаданные.


@sellers_router.put("/{Seller_id}")
async def update_Seller(Seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_Seller := await session.get(Seller, Seller_id):
        updated_Seller.first_name = new_data.first_name
        updated_Seller.last_name = new_data.last_name
        updated_Seller.email = new_data.email
        updated_Seller.books_for_sale = new_data.books_for_sale

        await session.flush()

        return updated_Seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
