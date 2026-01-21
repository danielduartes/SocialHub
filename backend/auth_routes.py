from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependencies import pegar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

# roteador -> quem organiza e registra as rotas
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# rota padrão de autenticação
@auth_router.get("/")
async def authenticate():
    return {"mensagem": "Você acessou a rota de autenticação.", "autenticado": False}


# rota para criar contas
@auth_router.post("/criar_conta")
# função assíncrona com os parâmetros sendo os campos a serem preenchidos na hora do cadastro
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    # verificar se já existe uma conta com o nome de usuário
    verificar_username = session.query(Usuario).filter(Usuario.username==usuario_schema.username).first()
    # verificar se já existe uma conta cadastrada com o e-mail 
    verificar_email = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    # função para calcular a idade do usuário na hora que ele preenche o formulário de cadastro
    def calcular_idade(data_nascimento: date) -> int:
        hoje = date.today()
        idade = hoje.year - data_nascimento.year

        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            idade -= 1

        return idade
    idade = calcular_idade(usuario_schema.data_nascimento)
    # mensagem caso o usuário já exista
    if verificar_username:
        raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado.")
    # mensagem caso o e-mail já tenha sido cadastrado
    elif verificar_email:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    elif idade < 15:
        raise HTTPException(status_code=400, detail="Sua idade não cumpre os requisitos para criar uma conta.")
    # mensagem de conta cadastrada com sucesso
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.username, usuario_schema.email, senha_criptografada, usuario_schema.data_nascimento)
        session.add(novo_usuario)
        session.commit()
        return {"mensagem": "Conta cadastrada com sucesso!"}