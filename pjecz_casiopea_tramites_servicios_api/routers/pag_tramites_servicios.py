"""
Pag Trámites y Servicios, routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.pag_tramites_servicios import PagTramiteServicio
from ..schemas.pag_tramites_servicios import OnePagTramitesServiciosOut, PagTramitesServiciosOut

pag_tramites_servicios = APIRouter(prefix="/api/v5/pag_tramites_servicios")


@pag_tramites_servicios.get("/{clave}", response_model=OnePagTramitesServiciosOut)
async def detalle(
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un Trámite o Servicio a partir de su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        pag_tramite_servicio = database.query(PagTramiteServicio).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OnePagTramitesServiciosOut(success=False, message="No existe ese trámite o servicio")
    if pag_tramite_servicio.es_activo is False:
        return OnePagTramitesServiciosOut(success=False, message="No está activo ese trámite o servicio")
    if pag_tramite_servicio.estatus != "A":
        return OnePagTramitesServiciosOut(success=False, message="Ese trámite o servicio está eliminado")
    return OnePagTramitesServiciosOut(
        success=True,
        message=f"Autoridad {clave}",
        data=PagTramitesServiciosOut.model_validate(pag_tramite_servicio),
    )


@pag_tramites_servicios.get("", response_model=CustomPage[PagTramitesServiciosOut])
async def paginado(
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de Trámites y Servicios"""
    return paginate(
        database.query(PagTramiteServicio).filter_by(es_activo=True).filter_by(estatus="A").order_by(PagTramiteServicio.clave)
    )
