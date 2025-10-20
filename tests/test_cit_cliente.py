"""
Unit tests for cit_clientes
"""

import unittest

import requests

from tests import config


class TestCitClientes(unittest.TestCase):
    """Tests for cit_clientes"""

    def test_get_cit_clientes_detalle(self):
        """Test GET method for cit_clientes detalle"""

        # Consultar
        response = requests.get(
            url=f"{config['api_base_url']}/cit_clientes/{config['cit_cliente_email']}",
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
        self.assertTrue("nombres" in item)
        self.assertTrue("apellido_primero" in item)
        self.assertTrue("apellido_segundo" in item)
        self.assertTrue("curp" in item)
        self.assertTrue("telefono" in item)
        self.assertTrue("email" in item)
        self.assertEqual(item["email"], config["cit_cliente_email"])


if __name__ == "__main__":
    unittest.main()
