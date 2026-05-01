import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient):
    payload = {
        "code": "  prod-001  ",
        "name": "  Monitor de Signos Vitales  ",
        "description": "Monitor multiparámetro avanzado",
        "price": 1250.50,
        "stock": 10
    }
    
    response = await client.post("/api/v1/products/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "PROD-001" # Should be cleaned and uppercase
    assert data["name"] == "Monitor de Signos Vitales" # Should be cleaned
    assert data["price"] == 1250.50
    assert "id" in data


@pytest.mark.asyncio
async def test_create_product_duplicate_code(client: AsyncClient, product_factory):
    # Pre-create a product
    await product_factory(code="PROD-DUP", name="Bisturí")
    
    payload = {
        "code": "PROD-DUP",
        "name": "Otro producto",
    }
    
    response = await client.post("/api/v1/products/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Product code already exists"


@pytest.mark.asyncio
async def test_get_products(client: AsyncClient, product_factory):
    await product_factory(code="P1", name="Product 1")
    await product_factory(code="P2", name="Product 2")
    
    response = await client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient, product_factory):
    product = await product_factory(code="P3", name="Product 3")
    
    response = await client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "P3"
    assert data["name"] == "Product 3"


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient, product_factory):
    product = await product_factory(code="P4", name="Product 4", price=10.0)
    
    update_payload = {
        "price": 15.0,
        "stock": 5
    }
    
    response = await client.patch(f"/api/v1/products/{product.id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 15.0
    assert data["stock"] == 5
    assert data["name"] == "Product 4" # Should remain unchanged


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient, product_factory, db_session: AsyncSession):
    product = await product_factory(code="P5", name="Product 5")
    
    response = await client.delete(f"/api/v1/products/{product.id}")
    assert response.status_code == 204
    
    # Check if logic delete worked (is_active = False)
    # The endpoint might return 404 for deleted or we can just fetch it directly to verify
    await db_session.refresh(product)
    assert product.is_active is False
