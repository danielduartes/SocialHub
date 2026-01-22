from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import Usuario
from dependencies import pegar_sessao, verificar_token
from main import bcrypt_context, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import date, datetime, timedelta, timezone

# roteador -> quem organiza e registra as rotas
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# função para criar o JWT (Json Web Token)
# token é como uma credencial digital temporária que autentica um usuário ou serviço e concede permissão para acessar recursos específicos do sistema
def criar_token(id_usuario, duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token # tempo de duração do JWT
    # dicionário com as informações necessárias para a autenticação 
    dic_info = {
        "sub": str(id_usuario),
        "exp": data_expiracao
    }
    # codificação do JWT com o ID do usuário (mais seguro)
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado

# função para verificar se as credenciais digitadas estão corretas
def autenticar_usuario(username, senha, session):
    usuario = session.query(Usuario).filter(Usuario.username==username).first() # buscando no banco o nome de usuário
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha, usuario.senha): # decodificando a senha que está no banco para saber se está correta
        return False
    return usuario


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


# rota de login do usuário
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    # chamando a função de autenticação do usuário colocando como parâmetro o nome e a senha digitados e a sessão para buscar no banco de dados as credenciais
    usuario = autenticar_usuario(login_schema.username, login_schema.senha, session)   
    # mensagem de erro se as credenciais estiverem erradas
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        # ao logar será gerado um access e um refresh token, o primeiro tendo 30 minutos de duração e outro 7 dias
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, duracao_token=timedelta(days=7))
        return {
            "acess_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }

@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    # chamando a função de autenticação do usuário colocando como parâmetro o nome e a senha digitados e a sessão para buscar no banco de dados as credenciais
    usuario = autenticar_usuario(dados_formulario.username, dados_formulario.password, session)   
    # mensagem de erro se as credenciais estiverem erradas
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas.")
    else:
        # ao logar será gerado um access tendo 30 minutos de tempo de expiração
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }

# rota de utilização do refresh token
# usa o refresh token quando o access token expira
@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    # chama a função de criar o access token
    access_token = criar_token(usuario.id)
    return {
            "access_token": access_token,
            "token_type": "Bearer"
        }