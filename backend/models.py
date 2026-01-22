from sqlalchemy import ForeignKey, create_engine, Column, String, Integer, Date, Boolean
from sqlalchemy.orm import declarative_base


# criando a conexão do banco
db = create_engine("sqlite:///../database/banco.db")

# base do banco de dados
Base = declarative_base()

# criar as classes/tabelas do banco

# tabela dos usuários
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column("username", String, unique=True, nullable=False)
    email = Column("email", String, unique=True, nullable=False)
    senha = Column("senha", String, nullable=False)
    data_nascimento = Column("data_nascimento", Date)
    seguidores = Column("seguidores", Integer, default=0)
    seguindo = Column("seguindo", Integer, default=0)
    posts = Column("posts", Integer, default=0)

    def __init__(self, username, email, senha, data_nascimento):
        self.username = username
        self.email = email
        self.senha = senha
        self.data_nascimento = data_nascimento


# tabela das postagens
class Post(Base):
    __tablename__ = "posts"

    id_post = Column("id_post", Integer, primary_key=True, autoincrement=True, nullable=False)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False)
    texto = Column("texto", String, nullable=True)
    foto = Column("foto", String, nullable=True, default=False)
    likes = Column("likes", Integer, default=0)

    def __init__(self, id_usuario, texto, foto):
        self.id_usuario = id_usuario
        self.texto = texto
        self.foto = foto

# executa a criação dos metadados do seu banco (cria efetivamente o banco de dados)