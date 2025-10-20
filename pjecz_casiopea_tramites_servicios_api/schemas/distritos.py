"""
Distritos, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class DistritoOut(BaseModel):
    """Esquema para entregar distritos"""

    clave: str
    nombre: str
    nombre_corto: str
    model_config = ConfigDict(from_attributes=True)


class OneDistritoOut(BaseModel):
    """Esquema para entregar un distrito"""

    success: bool
    message: str
    data: DistritoOut | None = None
