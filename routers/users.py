from fastapi import APIRouter, HTTPException #Clase con la que se intancia y se inicia la conexion
from pydantic import BaseModel #Clase para iniciar el modelo o entidad de alguna tabla o objeto del mundo real

router = APIRouter( tags=["users"], responses={404: {"Message": "No encontrado"}})

#Entidad user
#En primera instancia se esta generando el objeto para el tipo usuario con sus atributos y eso esta correcto, despues si no se utiliza el BaseModel lanzara errores ya que si tendremos los valores pero no el metodo contructor o el que ayuda a instaciar este objeto como tal y esa funcionalidad la da BaseModel
class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str | None = None
    age: int
    
#Como aun no tenemos base de datos creare una lista a mano que represente a la base de datos
users_list = [
    User(id= 1, name="John", surname="Doe", url="https://www.google.com", age=30),
    User(id= 2, name="Jane", surname="Doe", url="https://www.facebook.com", age=28),
    User(id= 3, name="Leonardo", surname="Garcia", url="https://www.facebook.com", age=19)
]

""" @app.get("/users")
async def users():
    return "Hello, users!" """

#Enviar solo el valor de la instanciación del usuario
@router.get("/usersClass")
async def usersClass():
    return User(name="John", surname="Doe", url="https://www.google.com", age=30),

#Enviar a la api una path con un parametro para filtrar
@router.get("/user/{id}")
async def get_user(id: int):
    return search_users(id)
#Ejemplo de parametros en el path
#http://127.0.0.1:8000/user/1

#Parametros query
@router.get("/userquery/", status_code=200)
async def get_user_query(id: int, name: str):
    return search_users(id)

#Enviar todos los valores de la lista de usuarios
@router.get("/users", status_code=200)
async def get_users():
    return users_list

#Protocolo http
#Protocolo post por lo general tiene como convención de que creara desde 0 un nuevo elemento
@router.post("/createUser", response_model=User, status_code=201)
async def user(user: User):
    if(type(search_users(user.id)) == User):
        #Con la libreria HTTPExcepyion traida del fastApi, se puede lanzar una excepcion
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    else:
        users_list.append(user)
        return user
    
#Protocolo put, es el encargado de actualizar mi elemento esa es su función
@router.put("/updateUser", status_code=200)
async def update_user(user: User):
    found = False 
    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            found = True
            users_list[index] = user
            return {"message": "El usuario se actualizo con exito"}
    
    if not found:
        raise HTTPException(status_code=409, detail="El usuario no fue actualizado")
    
@router.delete("/deleteUser/{id}", status_code=200)
async def delete_user(id: int):
    found = False
    for index, delete_user in enumerate(users_list):
        if delete_user.id == id:
            found = True
            del users_list[index]
            return {"message": "El usuario se ha eliminado con exito"}
        
    if not found:
        raise HTTPException(status_code=409, detail="El usuario no fue encontrado para eliminarlo")


def search_users(idUser: int):
    users = filter(lambda user: user.id == idUser, users_list)
    try: 
        return list(users)[0]
    except:
        return {"Error": "El usuario no fue encontrado"}

#Ejemplo de parametros query
#http://127.0.0.1:8000/userquery/?id=1 Sintaxis para cuando le envias solo un parametro
#http://127.0.0.1:8000/userquery/?id=1&name=bruno Sintaxis con varios parametros se debe dividir con el &
