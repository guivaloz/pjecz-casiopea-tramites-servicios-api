"""
Pag Tramites Servicios, modelos
"""

import uuid

from sqlalchemy import Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin


class PagTramiteServicio(Base, UniversalMixin):
    """PagTramiteServicio"""

    # Nombre de la tabla
    __tablename__ = "pag_tramites_servicios"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    costo: Mapped[Numeric] = mapped_column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    url: Mapped[str] = mapped_column(String(256))
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    pag_pagos: Mapped["PagPago"] = relationship("PagPago", back_populates="pag_tramite_servicio")

    def __repr__(self):
        """Representación"""
        return f"<PagTramiteServicio {self.clave}>"
