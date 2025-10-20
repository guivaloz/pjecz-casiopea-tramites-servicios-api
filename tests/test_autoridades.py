"""
Unit tests for autoridades
"""

import unittest

import requests

from tests import config


class TestAutoridades(unittest.TestCase):
    """Tests for autoridades"""

    def test_get_autoridades(self):
        """Test GET method for autoridades"""

        # Consultar
        response = requests.get(
            url=f"{config['api_base_url']}/autoridades",
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
            self.assertTrue("descripcion_corta" in item)
            self.assertTrue("distrito_clave" in item)
            self.assertTrue("distrito_nombre" in item)
            self.assertTrue("distrito_nombre_corto" in item)

    def test_get_autoridades_detalles(self):
        """Test GET method for autoridades detalle"""

        # Obtener claves de autoridades desde la configuración
        autoridades_claves = eval(config["autoridades_claves"])
        for autoridad_clave in autoridades_claves:
            # Consultar
            response = requests.get(
                url=f"{config['api_base_url']}/autoridades/{autoridad_clave}",
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
            self.assertTrue("descripcion_corta" in item)
            self.assertTrue("distrito_clave" in item)
            self.assertTrue("distrito_nombre" in item)
            self.assertTrue("distrito_nombre_corto" in item)


if __name__ == "__main__":
    unittest.main()
