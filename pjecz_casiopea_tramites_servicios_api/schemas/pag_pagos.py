"""
Pag Pagos, esquemas de pydantic
"""

from pydantic import BaseModel, ConfigDict


class PagPagoOut(BaseModel):
    """Esquema para entregar pagos"""

    id: str
    autoridad_clave: str
    autoridad_descripcion: str
    distrito_clave: str
    distrito_nombre: str
    cit_cliente_email: str
    cit_cliente_nombre: str
    pag_tramite_servicio_clave: str
    pag_tramite_servicio_descripcion: str
    cantidad: int
    descripcion: str
    estado: str
    folio: str
    resultado_tiempo: str | None = None
    total: float
    model_config = ConfigDict(from_attributes=True)


class OnePagPagoOut(BaseModel):
    """Esquema para entregar un pago"""

    success: bool
    message: str
    data: PagPagoOut | None = None


class PagCarroIn(BaseModel):
    """Esquema para recibir el carro de compras"""

    apellido_primero: str
    apellido_segundo: str | None = None
    nombres: str
    curp: str
    email: str
    telefono: str
    autoridad_clave: str
    distrito_clave: str
    pag_tramite_servicio_clave: str
    cantidad: int
    descripcion: str


class PagCarroOut(BaseModel):
    """Esquema para entregar el carro de compras"""

    id: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    email: str
    cantidad: int
    descripcion: str
    total: float
    url: str


class OnePagCarroOut(BaseModel):
    """Esquema para entregar un carro de compras"""

    success: bool
    message: str
    data: PagCarroOut | None = None


class PagResultadoIn(BaseModel):
    """Esquema para recibir el resultado del pago"""

    xml_encriptado: str | None


class PagResultadoOut(BaseModel):
    """Esquema para entregar un resultado del pago"""

    id: str
    autoridad_clave: str
    autoridad_descripcion: str
    autoridad_descripcion_corta: str
    distrito_clave: str
    distrito_nombre: str
    distrito_nombre_corto: str
    apellido_primero: str
    apellido_segundo: str | None = None
    nombres: str
    email: str
    estado: str
    folio: str
    resultado_tiempo: str | None = None
    total: float


class OnePagResultadoOut(BaseModel):
    """Esquema para entregar un resultado del pago"""

    success: bool
    message: str
    data: PagResultadoOut | None = None
