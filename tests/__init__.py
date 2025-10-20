"""
Tests Init
"""

import os

from dotenv import load_dotenv

load_dotenv()
config = {
    "api_base_url": os.getenv("API_BASE_URL", "http://127.0.0.1:8000"),
    "api_key": os.getenv("API_KEY", ""),
    "autoridades_claves": os.getenv("AUTORIDADES_CLAVES", "[]"),
    "cit_cliente_email": os.getenv("CIT_CLIENTE_EMAIL", ""),
    "distritos_claves": os.getenv("DISTRITOS_CLAVES", "[]"),
    "pag_tramites_servicios_claves": os.getenv("PAG_TRAMITES_SERVICIOS_CLAVES", "[]"),
    "timeout": int(os.getenv("TIMEOUT", "10")),
    "usuario_email": os.getenv("USUARIO_EMAIL", "anonymous@server.com"),
}
