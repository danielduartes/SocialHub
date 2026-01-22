from datetime import date
from fastapi import UploadFile, File
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


class PostSchema(BaseModel):
    id_usuario: int
    texto: Optional[str]
    foto: Optional[UploadFile] = File(None)

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    username: str
    senha: str

    class Config:
        from_attributes = True