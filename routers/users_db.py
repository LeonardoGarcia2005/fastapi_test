from fastapi import APIRouter, HTTPException, status
from db.models.User import User, DeleteUserRequest # Modelo de la base de datos
from db.schemas.user import user_schema_dict, users_schema_list  #Es una función que convierte los datos del modelo de usuario en un diccionario
from db.client import db_client #Conexion de la base de datos local
from bson import ObjectId #Cuando se genera el id en la base de datos de mongodb, se genera con el campo _id y es de tipo ObjectId, entonces siempre que tengamos que consultar debemos asegurarnos que el tipo de datos es ese

router = APIRouter( tags=["users_db"], responses={404: {"Message": "No encontrado"}})
    

@router.post("/createUserDb", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    find_user = search_user("email", user.email)
    
    if find_user != None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El nombre de usuario ya está en uso")
    
    user_dict = user.dict()
    del user_dict["id"]

    # Se ingresa dentro de mongo el usuario
    id_db = db_client.users.insert_one(user_dict).inserted_id

    # Se consulta el nuevo usuario creado
    new_user = user_schema_dict(db_client.users.find_one({"_id": ObjectId(id_db)}))
    if not new_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario")
    
    return User(**new_user)

@router.get("/getAllUsers", response_model=list[User], status_code=status.HTTP_200_OK)
async def get_all_users():
     # Obtiene todos los usuarios de la base de datos
    users = users_schema_list(db_client.users.find())
    return users

@router.get("/getUser/{id}", response_model=User, status_code=status.HTTP_200_OK)
async def getUser(id: str):
    user = search_user("_id", ObjectId(id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el usuario")
    return User(**user)

@router.delete("/deleteUser/", status_code=status.HTTP_200_OK)
async def delete_user(request: DeleteUserRequest):
    # Accede al ID desde el modelo
    id = request.id

    # Verifica si el ID es válido como ObjectId
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID proporcionado no es válido"
        )
    
    # Busca y elimina el usuario
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el usuario a eliminar"
        )
    
    return {"message": "Usuario eliminado con éxito"}

@router.put("/updateUser/{id}", response_model=User)
async def update_user(id: str, user: User):
    try:
        # Convierte el modelo `User` a un diccionario
        user_dict = user.dict()
        del user_dict["id"]

        # Busca y reemplaza el usuario en la base de datos, retornando el documento actualizado
        updated_user = db_client.users.find_one_and_replace(
            {"_id": ObjectId(id)},  # Busca por el ID recibido en la URL
            user_dict,              # Reemplaza con los datos del usuario recibido en el request body
            return_document=True    # Devuelve el documento actualizado
        )

        # Si no se encontró el usuario, lanza una excepción
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        # Convierte el `_id` a string y lo añade al modelo
        return User(
            id=str(updated_user["_id"]),  # Convertir ObjectId a string
            username=updated_user["username"],
            email=updated_user["email"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )

def search_user(field: str, key: str):
    user = db_client.users.find_one({field: key})
    if user:
        return user_schema_dict(user)
    return None