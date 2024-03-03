import pytest
from fastapi import status
from sqlalchemy import select

from src.models import sellers

result = {
    "sellers": [
        {"first_name": "fdhgdh", "last_name": "jdhdj", "email": "a@gmail.com", "books_for_sale": [{
        "id": 1,
        "title": "Wrong Code",
        "author": "Robert Martin",
        "count_pages": 104,
        "year": 2007,
        "seller_id": 1
    }]},
        {"first_name": "fdhgdfgfrh", "last_name": "jrrgdhdj", "email": "b@gmail.com", "books_for_sale": [{
        "id": 1,
        "title": "Clean Code",
        "author": "Robert Martin",
        "count_pages": 111,
        "year": 2017,
        "seller_id": 1
    }]},
    ]
}


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Alex", "last_name": "Ford", "email": "a@gmail.com", "password": "abc123", "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 1,
        "first_name": "Alex",
        "last_name": "Ford",
        "email": "a@gmail.com",
        "password": "abc123",
        "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller = sellers.Seller(first_name= "Alex", last_name = "Ford", email = "a@gmail.com",  books_for_sale = [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}])
    seller_2 = sellers.Seller(first_name= "Henry", last_name = "Ford", email = "b@gmail.com",  books_for_sale = [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}])

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Alex", "last_name": "Ford", "email": "a@gmail.com", "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]},
            {"first_name": "Henry", "last_name": "Ford", "email": "b@gmail.com", "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]},
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name= "Alex", last_name = "Ford", email = "a@gmail.com",  books_for_sale = [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}])
    seller_2 = sellers.Seller(first_name= "Henry", last_name = "Ford", email = "b@gmail.com",  books_for_sale = [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}])

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "Alex",
        "last_name": "Ford", 
        "email": "a@gmail.com", 
        "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):

    seller = sellers.Seller(first_name="Pushkin", last_name="Eugeny Onegin", year=2001, count_pages=104, seller_id= 1)

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):

    seller = sellers.Seller(first_name= "Alex", last_name = "Ford", email = "a@gmail.com",  books_for_sale = [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}])

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "Alex", "last_name": "Ford", "email": "a@gmail.com", "books_for_sale": [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "Alex"
    assert res.last_name == "Ford"
    assert res.email == "a@gmail.com"
    assert res.id == seller.id
    assert res.books_for_sale == [{"id": 1,"title": "Clean Code","author": "Robert Martin","count_pages": 111,"year": 2017,"seller_id": 1}]


