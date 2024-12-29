import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext #Libreria de hashing
from datetime import datetime, timedelta, timezone #Libreria encargada de trabajar con fechas, lo usaremos con el objetivo de poder validar o saber cuando se expire nuestro token, (datetime es para la fecha del sistema, y tomedelta es para realizar los calculos de fecha)

# Si queremos obtener una clave unica podemos correr este codigo para que me lanze una cadena al azar
# openssl rand -hex 32
SECRET_KEY = "c581177352e001e8d17685d710a74f65c93d58466a8545b7c2903009d1a3803c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["jwt_login"], responses={404: {"Message": "No encontrado"}})

oauth2 = OAuth2PasswordBearer(tokenUrl="jwt_login")

#Intanciacion de la libreria 
crypto = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDb(User):
    password: str

users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "disabled": False,
        "password": "$2y$10$0gllcreYKUrrDgPFqtod4.B9wdhCTtN6z./yuw7LC37lERad2TC.y"
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Johnson",
        "email": "alice@example.com",
        "disabled": False,
        "password": "$2y$10$RmOJBP387J5xBc0kI/NmeOK/8Iowhf0uBZcAnWFT3ZVkaqts7BnCO"
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Brown",
        "email": "bob@example.com",
        "disabled": False,
        "password": "$2y$10$6Jv0szabSNX4HX/58LOpv.I/uIe4Am83W6VSrmmd8ZEpqKmX28opW"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDb(**users_db[username]) # Usamos ** para descomponer el diccionario y crear una instancia de UserDb
    return None
    
def search_users(username: str):
    user_data = users_db.get(username)
    if user_data:
        return User(
            username=user_data["username"],
            full_name=user_data["full_name"],
            email=user_data["email"],
            disabled=user_data["disabled"]
        )
    return None

@router.post("/jwt_login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if user_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )
    
    user = search_user_db(form.username)
    
    # Los parametros que espera el crypto es la clava actual que nos envia el frontend, y la clave hasheada 
    if not crypto.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos"
        )
    
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = {
        "sub": user_db["username"],
        # Con el timestamp convertimos la fecha en segundos
        "exp": expiration
    }
    
    # Retornamos el token de acceso
    return {"access_token": jwt.encode(access_token, SECRET_KEY,algorithm=ALGORITHM), "token_type": "bearer"}

def auth_user(token: str = Depends(oauth2)):
    # Validar que el token no sea nulo o vacío
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Intentar decodificar el token usando la clave secreta y el algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Obtener el nombre de usuario del token
        username: str = payload.get("sub")
        
        # Validar que el token contenga un "sub" válido
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no contiene un usuario",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Lógica de autenticación (por ejemplo, buscar al usuario)
        user = search_users(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
    
    except ExpiredSignatureError:
        # El token ha expirado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    except InvalidTokenError:
        # Error general con el token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o corrupto",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario deshabilitado"
        )
    return user

@router.get("/users/jwt/me")
# Usamos Depends para asegurarnos de que el usuario esté autenticado
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user