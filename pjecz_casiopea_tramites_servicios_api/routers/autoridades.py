"""
Autoridades, routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.autoridades import Autoridad
from ..models.distritos import Distrito
from ..schemas.autoridades import AutoridadOut, OneAutoridadOut

autoridades = APIRouter(prefix="/api/v5/autoridades")


@autoridades.get("/{clave}", response_model=OneAutoridadOut)
async def detalle(
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de una autoridad a partir de su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        autoridad = database.query(Autoridad).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneAutoridadOut(success=False, message="No existe esa autoridad")
    if autoridad.es_activo is False:
        return OneAutoridadOut(success=False, message="No está activa esa autoridad")
    if autoridad.estatus != "A":
        return OneAutoridadOut(success=False, message="Esta autoridad está eliminada")
    return OneAutoridadOut(success=True, message="Detalle de una autoridad", data=AutoridadOut.model_validate(autoridad))


@autoridades.get("", response_model=CustomPage[AutoridadOut])
async def paginado(
    database: Annotated[Session, Depends(get_db)],
    distrito_clave: str = "",
):
    """Paginado de autoridades"""

    # Consultar autoridades
    consulta = database.query(Autoridad).join(Distrito)

    # Filtrar por los distritos donde es_distrito es True
    consulta = consulta.filter(Distrito.es_distrito == True)

    # Filtrar por distrito_clave si se proporciona
    if distrito_clave:
        distrito_clave = safe_clave(distrito_clave)
        if distrito_clave != "":
            consulta = consulta.filter(Distrito.clave == distrito_clave)

    # Filtrar por los activos
    consulta = consulta.filter(Autoridad.es_activo == True)

    # Filtrar por estatus "A"
    consulta = consulta.filter(Autoridad.estatus == "A")

    # Entregar
    return paginate(consulta.order_by(Autoridad.clave))
