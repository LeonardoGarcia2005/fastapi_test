from fastapi import APIRouter

# Con esto colocamos un prefijo para ya ahorrarnos colocar eso en el get de manera de que siempre realicemos algun path
router = APIRouter(prefix="/products", tags=["products"], responses={404: {"Message": "No encontrado"}})

product_list = [{"id": 1, "name": "Product 1", "price": 10.99}, { "id": 2, "name": "Product 2", "price": 15.99}, {"id": 3, "name": "Product 3", "price": 8.99}]

@router.get("/")
async def products():
    return product_list

@router.get("/{id}")
async def product(id: int):
    for index, one_product in enumerate(product_list):
        if one_product["id"] == id:
            return one_product
