from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: Optional[str]
    username: str
    email: str
    
# Modelo para el cuerpo de la solicitud
class DeleteUserRequest(BaseModel):
    id: str
