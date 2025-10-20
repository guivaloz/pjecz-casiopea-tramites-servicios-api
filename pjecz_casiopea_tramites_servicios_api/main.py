"""
PJECZ Casiopea Tramites Servicios API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from .config.settings import get_settings
from .routers.autoridades import autoridades
from .routers.cit_clientes import cit_clientes
from .routers.distritos import distritos
from .routers.pag_pagos import pag_pagos
from .routers.pag_tramites_servicios import pag_tramites_servicios

# FastAPI
app = FastAPI(
    title="PJECZ Casiopea Tramites Servicios API",
    description="API del Portal de Trámites y Servicios.",
    docs_url="/docs",
    redoc_url=None,
)

# CORSMiddleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ORIGINS.split(","),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rutas
app.include_router(autoridades)
app.include_router(cit_clientes)
app.include_router(distritos)
app.include_router(pag_pagos)
app.include_router(pag_tramites_servicios)

# Paginación
add_pagination(app)


# Mensaje de Bienvenida
@app.get("/")
async def root():
    """Mensaje de Bienvenida"""
    return {"message": "API del Portal de Trámites y Servicios."}
