from fastapi import APIRouter

# roteador -> quem organiza e registra as rotas
post_router = APIRouter(prefix="/post", tags=["post"])

@post_router.get("/")
async def posts():
    return {"mensagem": "Você acessou a rota de posts."}