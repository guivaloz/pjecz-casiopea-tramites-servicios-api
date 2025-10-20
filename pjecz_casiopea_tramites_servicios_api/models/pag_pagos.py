"""
Pag Pagos, modelos
"""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..dependencies.database import Base
from ..dependencies.universal_mixin import UniversalMixin


class PagPago(Base, UniversalMixin):
    """PagPago"""

    ESTADOS = {
        "SOLICITADO": "Solicitado",
        "CANCELADO": "Cancelado",
        "PAGADO": "Pagado",
        "FALLIDO": "Fallido",
        "ENTREGADO": "Entregado",
    }

    # Nombre de la tabla
    __tablename__ = "pag_pagos"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Claves foráneas
    autoridad_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="pag_pagos")
    distrito_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("distritos.id"))
    distrito: Mapped["Distrito"] = relationship(back_populates="pag_pagos")
    cit_cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cit_clientes.id"))
    cit_cliente: Mapped["CitCliente"] = relationship(back_populates="pag_pagos")
    pag_tramite_servicio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pag_tramites_servicios.id"))
    pag_tramite_servicio: Mapped["PagTramiteServicio"] = relationship(back_populates="pag_pagos")

    # Columnas
    caducidad: Mapped[date]
    cantidad: Mapped[int] = mapped_column(default=1)
    descripcion: Mapped[str] = mapped_column(String(256), default="")
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="pag_pagos_estados", native_enum=False), index=True)
    email: Mapped[str] = mapped_column(String(256))
    folio: Mapped[str] = mapped_column(String(256), default="")
    resultado_tiempo: Mapped[Optional[datetime]]
    resultado_xml: Mapped[Optional[str]] = mapped_column(Text)
    total: Mapped[Numeric] = mapped_column(Numeric(precision=8, scale=2, decimal_return_scale=2))
    ya_se_envio_comprobante: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        """Representación"""
        return f"<PagPago {self.id}>"
