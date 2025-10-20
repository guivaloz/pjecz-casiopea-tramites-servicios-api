"""
Distritos, routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.fastapi_pagination_custom_page import CustomPage
from ..dependencies.safe_string import safe_clave
from ..models.distritos import Distrito
from ..schemas.distritos import DistritoOut, OneDistritoOut

distritos = APIRouter(prefix="/api/v5/distritos")


@distritos.get("/{clave}", response_model=OneDistritoOut)
async def detalle(
    database: Annotated[Session, Depends(get_db)],
    clave: str,
):
    """Detalle de un distrito a partir de su clave"""
    try:
        clave = safe_clave(clave)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válida la clave")
    try:
        distrito = database.query(Distrito).filter_by(clave=clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OneDistritoOut(success=False, message="No existe ese distrito")
    if distrito.es_activo is False:
        return OneDistritoOut(success=False, message="No está activo ese distrito")
    if distrito.estatus != "A":
        return OneDistritoOut(success=False, message="Este distrito está eliminado")
    return OneDistritoOut(success=True, message="Detalle de un distrito", data=DistritoOut.model_validate(distrito))


@distritos.get("", response_model=CustomPage[DistritoOut])
async def paginado(
    database: Annotated[Session, Depends(get_db)],
):
    """Paginado de distritos"""

    # Consultar distritos
    consulta = database.query(Distrito)

    # Filtrar por es_distrito True
    consulta = consulta.filter_by(es_distrito=True)

    # Filtrar por los activos
    consulta = consulta.filter_by(es_activo=True)

    # Filtrar por estatus "A"
    consulta = consulta.filter_by(estatus="A")

    # Entregar
    return paginate(consulta.order_by(Distrito.clave))
