# Anotación de tipo
# El -> dict indica que la función devolverá un objeto de tipo diccionario
#Los esquemas son intermediarios para trabajar entre los modeles de la base de datos y la transformacion del json

def user_schema_dict(user) -> dict:
    return {"id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"]}

# Esta función transforma una lista de usuarios de la base de datos a una lista de diccionarios
# Esto es necesario para poder retornarlo
def users_schema_list(users) -> list:
    return [user_schema_dict(user) for user in users]