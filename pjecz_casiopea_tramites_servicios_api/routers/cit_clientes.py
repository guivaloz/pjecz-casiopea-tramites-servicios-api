"""
Cit Clientes, routers
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.safe_string import safe_email
from ..models.cit_clientes import CitCliente
from ..schemas.cit_clientes import CitClienteOut, OneCitClienteOut

cit_clientes = APIRouter(prefix="/api/v5/cit_clientes")


@cit_clientes.get("/{email}", response_model=OneCitClienteOut)
async def detalle(
    database: Annotated[Session, Depends(get_db)],
    email: str,
):
    """Detalle de un cit_cliente a partir de su email"""
    try:
        email = safe_email(email, search_fragment=False)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No es válido el email")
    try:
        cit_cliente = database.query(CitCliente).filter_by(email=email).one()
    except (MultipleResultsFound, NoResultFound):
        return OneCitClienteOut(success=False, message="No existe ese cliente")
    if cit_cliente.estatus != "A":
        return OneCitClienteOut(success=False, message="Este cliente está eliminado")
    return OneCitClienteOut(success=True, message="Detalle de un cliente", data=CitClienteOut.model_validate(cit_cliente))
