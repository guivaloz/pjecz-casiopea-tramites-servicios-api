"""
Unit tests for distritos
"""

import unittest

import requests

from tests import config


class TestDistritos(unittest.TestCase):
    """Tests for distritos"""

    def test_get_distritos(self):
        """Test GET method for distritos"""

        # Consultar
        response = requests.get(
            url=f"{config['api_base_url']}/distritos",
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
            self.assertTrue("nombre" in item)
            self.assertTrue("nombre_corto" in item)

    def test_get_distritos_detalles(self):
        """Test GET method for distritos detalle"""

        # Obtener claves de distritos desde la configuración
        distritos_claves = eval(config["distritos_claves"])
        for distrito_clave in distritos_claves:
            # Consultar
            response = requests.get(
                url=f"{config['api_base_url']}/distritos/{distrito_clave}",
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
            self.assertTrue("nombre" in item)
            self.assertTrue("nombre_corto" in item)


if __name__ == "__main__":
    unittest.main()
