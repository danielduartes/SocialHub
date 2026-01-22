import http
from sqlalchemy.orm import sessionmaker, Session
from models import db, Usuario
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_schema


def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session # 'yield' retorna um valor mas não termina a função
    finally: # 'finally' executa a função de 'close' dando certo ou errado
        session.close()

# função de verificação do token
# a verificação de token funciona como um "bilhete de acesso" digital: após o login inicial, o servidor emite um token (código único e temporário) para o usuário, provando sua identidade sem exigir senha a cada passo, sendo validado em solicitações subsequentes até expirar ou o usuário sair
def verificar_token(token: str = Depends(oauth2_schema), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso Negado, verifique a validade do token.")
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first() # fazendo a busca no banco de dados
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido.")
    return usuario