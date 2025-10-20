"""
Cit Clientes, esquemas de pydantic
"""

import uuid

from pydantic import BaseModel, ConfigDict


class CitClienteOut(BaseModel):
    """Esquema para entregar clientes"""

    nombres: str
    apellido_primero: str
    apellido_segundo: str
    curp: str
    telefono: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class OneCitClienteOut(BaseModel):
    """Esquema para entregar un cliente"""

    success: bool
    message: str
    data: CitClienteOut | None = None
