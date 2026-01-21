from datetime import date
from pydantic import BaseModel
from typing import Optional

class UsuarioSchema(BaseModel):
    username: str
    email: str
    senha: str
    data_nascimento: date

    # indica que o 'UsuarioSchema' não vai ser interpretado como um dicionário convencional, e sim um ORM
    class Config: 
        from_attributes = True