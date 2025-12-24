from fastapi import FastAPI
from .routers.clients import router as clients_router
from .routers.train import router as train_router

app = FastAPI(title="FastIA API", version="2.0.0")
app.include_router(clients_router)
app.include_router(train_router)
