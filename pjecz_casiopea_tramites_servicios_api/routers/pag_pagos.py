"""
Pag Pagos, routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.pag_pagos import PagPago
from ..schemas.pag_pagos import (
    OnePagCarroOut,
    OnePagPagoOut,
    OnePagResultadoOut,
    PagCarroIn,
    PagCarroOut,
    PagPagoOut,
    PagResultadoIn,
    PagResultadoOut,
)

pag_pagos = APIRouter(prefix="/api/v5/pag_pagos")


@pag_pagos.post("/carro", response_model=OnePagCarroOut)
async def carro(
    database: Annotated[Session, Depends(get_db)],
    datos: PagCarroIn,
):
    """Recibir, procesar y entregar datos del carro de pagos"""


@pag_pagos.post("/resultado", response_model=OnePagResultadoOut)
async def resultado(
    database: Annotated[Session, Depends(get_db)],
    datos: PagResultadoIn,
):
    """Recibir, procesar y entregar datos del resultado de pagos"""


@pag_pagos.get("/{pag_pago_id}", response_model=OnePagPagoOut)
async def detalle_pag_pago(
    database: Annotated[Session, Depends(get_db)],
    pag_pago_id: str,
):
    """Detalle de un pago a partir de su UUID"""
