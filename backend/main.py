from fastapi import FastAPI
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI()

# agente que vai fazer a criptografia da senha dos usuários cadastrados
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from auth_routes import auth_router
from post_routes import post_router

# falando para o app incluir todos os roteadores
app.include_router(auth_router)
app.include_router(post_router)

# para rodar o nosso código, executar no terminal: uvicorn main:app --reload