from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import PostSchema
from models import Post
import shutil
import os


# roteador -> quem organiza e registra as rotas
post_router = APIRouter(prefix="/post", tags=["post"])

# rota padrão dos posts
@post_router.get("/")
async def posts():
    return {"mensagem": "Você acessou a rota de posts."}

# upload de fotos para os posts
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# rota de publicação de posts
@post_router.post("/posts")
async def criar_post(post_schema: PostSchema, session: Session = Depends(pegar_sessao)):
    path_foto = None
    if post_schema.foto:
        path_foto = os.path.join(UPLOAD_DIR, post_schema.foto.filename)
        with open(path_foto, "wb") as buffer:
            shutil.copyfileobj(post_schema.foto.file, buffer)
    novo_post = Post(id_usuario=post_schema.id_usuario, texto=post_schema.texto, foto=post_schema.foto)
    session.add(novo_post)
    session.commit()
    return {"mensagem": f"Post publicado com sucesso. ID do post: {novo_post.id_post}"}