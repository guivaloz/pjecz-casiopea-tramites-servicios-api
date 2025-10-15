"""
Pag Tramites Servicios, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class PagTramitesServiciosOut(BaseModel):
    """Esquema para entregar pag_tramites_servicios"""

    clave: str
    descripcion: str
    costo: float
    url: str
    es_activo: bool
    model_config = ConfigDict(from_attributes=True)


class OnePagTramiteServicioOut(BaseModel):
    """Esquema para entregar un pag_tramite_servicio"""

    success: bool
    message: str
    data: PagTramitesServiciosOut | None = None
