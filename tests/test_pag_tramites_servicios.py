"""
Unit tests for pag tramites servicios
"""

import unittest

import requests

from tests import config


class TestPagTramitesServicios(unittest.TestCase):
    """Tests for pag_tramites_servicios"""

    def test_get_pag_tramites_servicios(self):
        """Test GET method for pag_tramites_servicios"""

        # Consultar
        response = requests.get(
            url=f"{config['api_base_url']}/pag_tramites_servicios",
            headers={"X-Api-Key": config["api_key"]},
            timeout=config["timeout"],
        )
        self.assertEqual(response.status_code, 200)

        # Validar contenido
        contenido = response.json()
        self.assertTrue("success" in contenido)
        self.assertTrue(contenido["success"])
        self.assertTrue("message" in contenido)
        self.assertTrue("data" in contenido)

        # Validar datos
        self.assertTrue(isinstance(contenido["data"], list))
        for item in contenido["data"]:
            self.assertTrue("clave" in item)
            self.assertTrue("descripcion" in item)
            self.assertTrue("costo" in item)
            self.assertTrue("url" in item)

    def test_get_pag_tramites_servicios_detalles(self):
        """Test GET method for pag_tramites_servicios detalle"""

        # Obtener claves de pag_tramites_servicios desde la configuración
        pag_tramites_servicios_claves = eval(config.get("pag_tramites_servicios_claves"))
        for pag_tramite_servicio_clave in pag_tramites_servicios_claves:
            # Consultar
            response = requests.get(
                url=f"{config['api_base_url']}/pag_tramites_servicios/{pag_tramite_servicio_clave}",
                headers={"X-Api-Key": config["api_key"]},
                timeout=config["timeout"],
            )
            self.assertEqual(response.status_code, 200)

            # Validar contenido
            contenido = response.json()
            self.assertTrue("success" in contenido)
            self.assertTrue(contenido["success"])
            self.assertTrue("message" in contenido)
            self.assertTrue("data" in contenido)

            # Validar datos
            item = contenido["data"]
            self.assertTrue("clave" in item)
            self.assertTrue("descripcion" in item)
            self.assertTrue("costo" in item)
            self.assertTrue("url" in item)


if __name__ == "__main__":
    unittest.main()
