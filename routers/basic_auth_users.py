from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel  # Con el BaseModel nos permite de manera muy sencilla poder pasar este objeto a la red y que tenga su conversión de manera automática a JSON

router = APIRouter(tags=["basic_login"], responses={404: {"Message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="basic_login")  # Se instancia la clase para la autenticación, este es el encargado de validar las credenciales

# Entidad que retornaremos al cliente desde el programa sin la contraseña
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

# Hacemos que UserDb herede de User para añadir la propiedad "password" que no retornaremos al cliente
class UserDb(User):
    password: str

# Base de datos simulada
users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "disabled": False,
        "password": "123456"
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "disabled": False,
        "password": "secret"
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Brown",
        "email": "bob@example.com",
        "disabled": False,
        "password": "password"
    }
}

# Función para buscar un usuario en la base de datos
def search_users(username: str):
    user_data = users_db.get(username)
    if user_data:
        return User(**user_data)  # Usamos ** para descomponer el diccionario y crear una instancia de UserDb
    return None

# Verifica que la contraseña proporcionada coincida con la almacenada.
def verify_password(stored_password: str, provided_password: str) -> bool:
    return stored_password == provided_password

# Función encargada de validar el token que regresa la autenticación
def get_current_user(token: str = Depends(oauth2)):
    user = search_users(token)  # En este caso, usamos el token como si fuera el nombre del usuario (por simplicidad)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario deshabilitado"
        )
    return user

@router.post("/basic_login")
# Usamos Depends para manejar automáticamente los datos enviados en el formulario
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )

    # Comparamos la contraseña ingresada con la contraseña almacenada en la base de datos
    if not verify_password(user_db["password"], form.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )

    # Retornamos el token de acceso
    return {"access_token": user_db["username"], "token_type": "bearer"}

@router.get("/users/basic/me")
# Usamos Depends para asegurarnos de que el usuario esté autenticado
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user