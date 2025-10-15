"""
Pag Pagos, routers
"""

from datetime import datetime, timedelta
from typing import Annotated

import nest_asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from ..dependencies.database import Session, get_db
from ..dependencies.safe_string import safe_clave, safe_curp, safe_email, safe_integer, safe_string, safe_telefono
from ..dependencies.santander_web_pay_plus import SantanderWebPayPlusAnyError, create_pay_link
from ..models.autoridades import Autoridad
from ..models.cit_clientes import CitCliente
from ..models.distritos import Distrito
from ..models.pag_pagos import PagPago
from ..models.pag_tramites_servicios import PagTramiteServicio
from ..schemas.pag_pagos import (
    OnePagCarroOut,
    OnePagPagoOut,
    OnePagResultadoOut,
    PagCarroIn,
    PagCarroOut,
    PagPagoOut,
    PagResultadoIn,
    PagResultadoOut,
)

pag_pagos = APIRouter(prefix="/api/v5/pag_pagos")


@pag_pagos.post("/carro", response_model=OnePagCarroOut)
async def carro(
    database: Annotated[Session, Depends(get_db)],
    pag_carro_in: PagCarroIn,
):
    """Recibir, procesar y entregar datos del carro de pagos"""

    # Validar nombres
    nombres = safe_string(pag_carro_in.nombres, save_enie=True)
    if nombres == "":
        return OnePagCarroOut(success=False, message="El nombre no es válido")

    # Validar apellido_primero
    apellido_primero = safe_string(pag_carro_in.apellido_primero, save_enie=True)
    if apellido_primero == "":
        return OnePagCarroOut(success=False, message="El primer apellido no es válido")

    # Es opcional el apellido_segundo
    apellido_segundo = safe_string(pag_carro_in.apellido_segundo, save_enie=True)

    # Validar curp
    try:
        curp = safe_curp(pag_carro_in.curp)
    except ValueError:
        return OnePagCarroOut(success=False, message="La CURP no es válida")

    # Validar email
    try:
        email = safe_email(pag_carro_in.email)
    except ValueError:
        return OnePagCarroOut(success=False, message="El correo electrónico no es válido")

    # Validar teléfono
    try:
        telefono = safe_telefono(pag_carro_in.telefono)
    except ValueError:
        return OnePagCarroOut(success=False, message="El teléfono no es válido")

    # Validar pag_tramite_servicio_clave
    try:
        pag_tramite_servicio_clave = safe_clave(pag_carro_in.pag_tramite_servicio_clave)
    except ValueError:
        return OnePagCarroOut(success=False, message="La clave del trámite o servicio no es válida")
    try:
        pag_tramite_servicio = database.query(PagTramiteServicio).filter_by(clave=pag_tramite_servicio_clave).one()
    except (MultipleResultsFound, NoResultFound):
        return OnePagCarroOut(success=False, message="No existe ese trámite o servicio")
    if pag_tramite_servicio.es_activo is False:
        return OnePagCarroOut(success=False, message="No está activo ese trámite o servicio")
    if pag_tramite_servicio.estatus != "A":
        return OnePagCarroOut(success=False, message="Ese trámite o servicio está eliminado")

    # Validar autoridad_clave
    if pag_carro_in.autoridad_clave:
        try:
            autoridad_clave = safe_clave(pag_carro_in.autoridad_clave)
        except ValueError:
            return OnePagCarroOut(success=False, message="La clave de la autoridad no es válida")
        try:
            autoridad = database.query(Autoridad).filter_by(clave=autoridad_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return OnePagCarroOut(success=False, message="No existe esa autoridad")
        if autoridad.es_activo is False:
            return OnePagCarroOut(success=False, message="No está activa esa autoridad")
        if autoridad.estatus != "A":
            return OnePagCarroOut(success=False, message="Esta autoridad está eliminada")
    else:
        # Si no se proporciona, usar la autoridad ND (NO DEFINIDO)
        autoridad = database.query(Autoridad).filter_by(clave="ND").one()

    # Validar distrito_clave
    if pag_carro_in.distrito_clave:
        try:
            distrito_clave = safe_clave(pag_carro_in.distrito_clave)
        except ValueError:
            return OnePagCarroOut(success=False, message="La clave del distrito no es válida")
        try:
            distrito = database.query(Distrito).filter_by(clave=distrito_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return OnePagCarroOut(success=False, message="No existe ese distrito")
        if distrito.es_activo is False:
            return OnePagCarroOut(success=False, message="No está activo ese distrito")
        if distrito.estatus != "A":
            return OnePagCarroOut(success=False, message="Este distrito está eliminado")
    else:
        # Si no se proporciona, usar el distrito de la autoridad
        distrito = autoridad.distrito

    # Validar la cantidad
    cantidad = safe_integer(pag_carro_in.cantidad, default=1)  # Valor por defecto 1

    # Validar la descripción
    descripcion = safe_string(pag_carro_in.descripcion, save_enie=True)
    if descripcion == "":
        descripcion = pag_tramite_servicio.descripcion
    else:
        descripcion = f"{pag_tramite_servicio.descripcion} - {descripcion}"

    # Calcular y validar el total
    total = pag_tramite_servicio.costo * cantidad
    if total <= 0:
        return OnePagCarroOut(success=False, message="El total no es válido")

    # Validar el CURP
    try:
        curp = safe_curp(curp)
    except ValueError:
        return OnePagCarroOut(success=False, message="La CURP no es válida")

    # Validar el email
    try:
        email = safe_email(email)
    except ValueError:
        return OnePagCarroOut(success=False, message="El correo electrónico no es válido")

    # Buscar al cit_cliente, primero por CURP y luego por email
    cit_cliente = None
    try:
        cit_cliente = database.query(CitCliente).filter_by(curp=curp).one()
    except (MultipleResultsFound, NoResultFound):
        try:
            cit_cliente = database.query(CitCliente).filter_by(email=email).one()
        except (MultipleResultsFound, NoResultFound):
            cit_cliente = None

    # Si no existe, crear al cit_cliente
    if cit_cliente is None:
        renovacion_fecha = datetime.now() + timedelta(days=60)
        try:
            cit_cliente = CitCliente(
                nombres=nombres,
                apellido_primero=apellido_primero,
                apellido_segundo=apellido_segundo,
                curp=curp,
                telefono=telefono,
                email=email,
                contrasena_md5="",
                contrasena_sha256="",
                renovacion=renovacion_fecha.date(),
                limite_citas_pendientes=3,
            )
            database.add(cit_cliente)
            database.commit()
            database.refresh(cit_cliente)
        except Exception:
            database.rollback()
            return OnePagCarroOut(success=False, message="No se pudo crear el cliente")

    # Definir la fecha de caducidad que sea dentro de 30 días
    caducidad = datetime.now() + timedelta(days=30)

    # Insertar pago
    pag_pago = PagPago(
        autoridad=autoridad,
        distrito=distrito,
        cit_cliente=cit_cliente,
        pag_tramite_servicio=pag_tramite_servicio,
        caducidad=caducidad.date(),
        cantidad=cantidad,
        descripcion=descripcion,
        email=email,
        estado="SOLICITADO",
        total=total,
        ya_se_envio_comprobante=False,
    )
    database.add(pag_pago)
    database.commit()
    database.refresh(pag_pago)

    # Crear URL al banco
    nest_asyncio.apply()
    try:
        url = create_pay_link(
            pago_id=pag_pago.id,
            email=email,
            service_detail=pag_tramite_servicio.descripcion,
            cit_client_id=cit_cliente.id,
            amount=float(total),
        )
    except SantanderWebPayPlusAnyError as error:
        return OnePagCarroOut(success=False, message=f"No se pudo crear el enlace de pago: {error}")

    # Entregar
    pag_carro_out = PagCarroOut(
        id=pag_pago.id,
        autoridad_clave=autoridad.clave,
        autoridad_descripcion=autoridad.descripcion,
        autoridad_descripcion_corta=autoridad.descripcion_corta,
        cantidad=cantidad,
        descripcion=descripcion,
        distrito_clave=distrito.clave,
        distrito_nombre=distrito.nombre,
        distrito_nombre_corto=distrito.nombre_corto,
        email=email,
        total=total,
        url=url,
    )
    return OnePagCarroOut(success=True, message="Carro de compras creado", data=pag_carro_out)


@pag_pagos.post("/resultado", response_model=OnePagResultadoOut)
async def resultado(
    database: Annotated[Session, Depends(get_db)],
    pag_resultado_in: PagResultadoIn,
):
    """Recibir, procesar y entregar datos del resultado de pagos"""


@pag_pagos.get("/{pag_pago_id}", response_model=OnePagPagoOut)
async def detalle_pag_pago(
    database: Annotated[Session, Depends(get_db)],
    pag_pago_id: str,
):
    """Detalle de un pago a partir de su UUID"""
