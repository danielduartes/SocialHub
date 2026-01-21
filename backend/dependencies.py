from sqlalchemy.orm import session, sessionmaker
from models import db


def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session # 'yield' retorna um valor mas não termina a função
    finally: # 'finally' executa a função de 'close' dando certo ou errado
        session.close()