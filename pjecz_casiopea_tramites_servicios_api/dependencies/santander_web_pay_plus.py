"""
Santander Web Pay Plus
"""

import asyncio
import os
import re
import urllib
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv

from .AESEncryption import AES128Encryption

XML_ENCRYPT_REGEXP = r"^[a-zA-Z0-9=+\/]{32,}$"

RESPUESTA_EXITO = "approved"
RESPUESTA_DENEGADA = "denied"
RESPUESTA_ERROR = "error"

load_dotenv()
WPP_COMMERCE_ID = os.getenv("WPP_COMMERCE_ID", None)
WPP_COMPANY_ID = os.getenv("WPP_COMPANY_ID", None)
WPP_BRANCH_ID = os.getenv("WPP_BRANCH_ID", None)
WPP_KEY = os.getenv("WPP_KEY", None)
WPP_PASS = os.getenv("WPP_PASS", None)
WPP_TIMEOUT = int(os.getenv("WPP_TIMEOUT", "12"))
WPP_URL = os.getenv("WPP_URL", None)
WPP_USER = os.getenv("WPP_USER", None)


class SantanderWebPayPlusAnyError(Exception):
    """Base exception class"""


class SantanderWebPayPlusBankResponseInvalidError(SantanderWebPayPlusAnyError):
    """Error en la respuesta del banco"""


class SantanderWebPayPlusConnectionError(SantanderWebPayPlusAnyError):
    """Error de conexión con el banco"""


class SantanderWebPayPlusDesencryptError(SantanderWebPayPlusAnyError):
    """Error al desencriptar la respuesta del banco"""


class SantanderWebPayPlusEncryptError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusGetURLFromXMLEncryptedError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusMissingConfigurationError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusNotValidAnswerError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusRequestError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusTimeoutError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusUnknownError(SantanderWebPayPlusAnyError):
    """Error"""


class SantanderWebPayPlusXMLReadError(SantanderWebPayPlusAnyError):
    """Error"""


def create_chain_xml(
    pago_id: int,
    amount: float,
    email: str,
    description: str,
    cit_client_id: int,
) -> str:
    """Crear cadena XML"""

    # Validar WPP_COMPANY_ID
    if WPP_COMPANY_ID is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_COMPANY_ID.")

    # Validar WPP_BRANCH_ID
    if WPP_BRANCH_ID is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_BRANCH_ID.")

    # Validar WPP_USER
    if WPP_USER is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_USER.")

    # Validar WPP_PASS
    if WPP_PASS is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_PASS.")

    # Inicializar XML
    root = ET.Element("P")

    # Inicializar datos de la organización
    business = ET.SubElement(root, "business")
    ET.SubElement(business, "id_company").text = WPP_COMPANY_ID
    ET.SubElement(business, "id_branch").text = WPP_BRANCH_ID
    ET.SubElement(business, "user").text = WPP_USER
    ET.SubElement(business, "pwd").text = WPP_PASS

    # Inicializar datos de la version
    ET.SubElement(root, "version").text = "IntegraWPP"

    # Inicializar datos del cliente y del pago
    url = ET.SubElement(root, "url")
    ET.SubElement(url, "reference").text = str(pago_id)
    ET.SubElement(url, "amount").text = str(amount)
    ET.SubElement(url, "moneda").text = "MXN"
    ET.SubElement(url, "canal").text = "W"
    ET.SubElement(url, "omitir_notif_default").text = "0"
    ET.SubElement(url, "st_correo").text = "1"
    ET.SubElement(url, "mail_cliente").text = email

    # Inicializar datos adicionales
    data = ET.SubElement(url, "datos_adicionales")

    # Inicializar descripción del servicio
    data1 = ET.SubElement(data, "data")
    data1.attrib["id"] = "1"
    data1.attrib["display"] = "true"
    label1 = ET.SubElement(data1, "label")
    label1.text = "Servicio"
    value1 = ET.SubElement(data1, "value")
    value1.text = description

    # Inicializar descripción del cliente
    data2 = ET.SubElement(data, "data")
    data2.attrib["id"] = "2"
    data2.attrib["display"] = "false"
    label2 = ET.SubElement(data2, "label")
    label2.text = "Cliente ID"
    value2 = ET.SubElement(data2, "value")
    value2.text = str(cit_client_id)

    # Entregar cadena XML
    return ET.tostring(root, encoding="unicode")


def encrypt_chain(chain: str) -> str:
    """Cifrar cadena XML"""

    # Validar WPP_KEY
    if WPP_KEY is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_KEY.")

    # Cifrar la cadena
    aes_encryptor = AES128Encryption()
    ciphertext = aes_encryptor.encrypt(chain, WPP_KEY)

    # Entregar cadena cifrada
    return ciphertext


def decrypt_chain(chain_encrypted: str) -> str:
    """Descifrar cadena XML"""

    # Validar WPP_KEY
    if WPP_KEY is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_KEY.")

    # Eliminar avances de línea y espacios en blanco
    chain_encrypted = chain_encrypted.replace("\n", "").replace(" ", "")

    # Validar la cadena cifrada con la expresión regular
    if re.fullmatch(XML_ENCRYPT_REGEXP, chain_encrypted) is None:
        raise SantanderWebPayPlusBankResponseInvalidError(
            f"Error porque la respuesta del banco no pasa la validación por expresión regular: [{chain_encrypted}]"
        )

    # Descifrar la cadena
    aes_encryptor = AES128Encryption()
    try:
        plaintext = aes_encryptor.decrypt(WPP_KEY, chain_encrypted)
    except Exception as error:
        raise SantanderWebPayPlusDesencryptError("Error porque no se pudo desencritar la respuesta del banco.") from error

    # Entregar cadena descifrada
    return plaintext


def create_chain_xml_sender(chain: str) -> str:
    """Crear cadena para XML de envío WPP"""

    # Validar WPP_COMMERCE_ID
    if WPP_COMMERCE_ID is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_COMMERCE_ID.")

    # Validar WPP_URL
    if WPP_URL is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_URL.")

    # Empacar la cadena
    root = ET.Element("pgs")
    ET.SubElement(root, "data0").text = WPP_COMMERCE_ID
    ET.SubElement(root, "data").text = chain
    chain_bytes = ET.tostring(root, encoding="unicode")

    # Entregar cadena
    return urllib.parse.quote(chain_bytes, "utf-8")


async def send_chain(chain: str) -> str:
    """Enviar cadena a WPP"""

    # Validar WPP_URL
    if WPP_URL is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_URL.")

    # Validar WPP_TIMEOUT
    if WPP_TIMEOUT is None:
        raise SantanderWebPayPlusMissingConfigurationError("Falta declarar la variable de entorno WPP_TIMEOUT.")

    # Preparar la carga para la petición
    payload = "xml=" + create_chain_xml_sender(chain)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Enviar la petición al banco
    try:
        response = requests.request(
            "POST",
            WPP_URL,
            headers=headers,
            data=payload,
            timeout=WPP_TIMEOUT,
        )
    except requests.exceptions.ConnectionError as error:
        raise SantanderWebPayPlusConnectionError("Error porque no se pudo conectar al banco.") from error
    except requests.exceptions.Timeout as error:
        raise SantanderWebPayPlusTimeoutError("Error porque se agoto el tiempo de espera con el banco.") from error
    except requests.exceptions.RequestException as error:
        raise SantanderWebPayPlusRequestError("Error al enviar la cadena al banco.") from error
    except Exception as error:
        raise SantanderWebPayPlusUnknownError("Error desconocido al enviar la cadena al banco.") from error

    # Entregar
    return response.text


def get_url_from_xml_encrypt(xml_encrypt: str):
    """Extrae la url del xml de respuesta"""

    # Desencriptar el XML
    try:
        xml_str = decrypt_chain(xml_encrypt)
    except Exception as error:
        raise SantanderWebPayPlusDesencryptError(f"No se puede desencriptar el XML del banco. {str(error)}") from error

    # Leer el contenido XML
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as error:
        raise SantanderWebPayPlusXMLReadError("Error porque el XML del banco no es válido.") from error

    # Obtener el URL
    url = root.find("nb_url").text
    if url is None or url == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML del banco no tiene la URL.")

    # Entregar
    return url


def create_pay_link(
    pago_id: int,
    email: str,
    service_detail: str,
    cit_client_id: int,
    amount: float,
) -> str:
    """Regresa el link para mostrar el formulario de pago"""

    # Crear cadena XML
    chain = create_chain_xml(
        pago_id=pago_id,
        amount=amount,
        email=email,
        description=service_detail,
        cit_client_id=cit_client_id,
    )

    # Encriptación del XML
    try:
        chain_encrypt = encrypt_chain(chain).decode()  # bytes
    except Exception as error:
        raise SantanderWebPayPlusEncryptError("Error al encriptar el XML") from error

    # Enviar cadena XML a WPP
    respuesta = None
    try:
        respuesta = asyncio.run(send_chain(chain_encrypt))
    except asyncio.TimeoutError as error:
        raise SantanderWebPayPlusTimeoutError("Error porque se agoto el tiempo de espera con el banco.") from error
    except Exception as error:
        raise SantanderWebPayPlusUnknownError("Error al tratar de enviar la cadena XML al banco.") from error

    # Si no hay respuesta, causar error
    if respuesta is None or respuesta == "" or respuesta == "\n":
        raise SantanderWebPayPlusNotValidAnswerError("Error en la respuesta del banco (respuesta vacía).")

    # Descifrar la respuesta y extraer la url
    try:
        url = get_url_from_xml_encrypt(respuesta)
    except Exception as error:
        raise SantanderWebPayPlusGetURLFromXMLEncryptedError(
            f"Error al obtener la URL del banco desde su XML encriptado. {str(error)}"
        ) from error

    # Entregar
    return url


def convert_xml_to_dict(xml_str: str) -> dict:
    """Convertir el xml descifrado a un diccionario"""

    # Leer el contenido XML
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as error:
        raise SantanderWebPayPlusXMLReadError("Error porque el XML que dio el banco no es válido.") from error

    # Obtener pago_id
    pago_id = root.find("reference").text
    if pago_id is None or pago_id == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML no tiene el pago_id.")

    # Obtener respuesta
    respuesta = root.find("response").text
    if respuesta is None or respuesta == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML no tiene la respuesta.")

    # Obtener folio
    folio = root.find("foliocpagos").text
    if folio is None or folio == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML no tiene el folio.")

    # Obtener auth
    auth = root.find("auth").text
    if auth is None or auth == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML no tiene el auth.")

    # Obtener email
    email = root.find("email").text
    if email is None or email == "":
        raise SantanderWebPayPlusXMLReadError("Error porque el XML no tiene el email.")

    # Entregar diccionario
    return {
        "pago_id": pago_id,
        "respuesta": respuesta,
        "folio": folio,
        "auth": auth,
        "email": email,
    }
