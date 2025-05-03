import requests
import json
import base64
import time
from core.utils import generate_random_string


class CalderaClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"KEY": api_key, "Content-Type": "application/json"}

    def test_connection(self):
        """Prueba la conexión con el servidor Caldera"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v2/abilities", headers=self.headers, verify=False
            )

            if response.status_code == 200:
                return True, "Conexión exitosa"
            else:
                return False, f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"

    def get_abilities(self):
        """Obtiene todas las habilidades disponibles en Caldera"""
        response = requests.get(
            f"{self.base_url}/api/v2/agents", headers=self.headers, verify=False
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_adversaries(self):
        """Obtiene todos los perfiles de adversarios disponibles"""
        response = requests.get(
            f"{self.base_url}/api/v2/adversaries", headers=self.headers, verify=False
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def get_agents(self):
        """Obtiene todos los agentes conectados"""
        response = requests.get(
            f"{self.base_url}/api/v2/agents", headers=self.headers, verify=False
        )

        return response.json()

    def deploy_agent(self):
        messages = [
            "\n[!] La API de Caldera v5.3.0 no soporta la generación automática del agente Sandcat.",
            "[*] Por favor, ve a la interfaz web de Caldera y genera el comando de despliegue manualmente:",
            "    Caldera UI → Agents → Deploy → Selecciona plataforma y copia el comando generado.\n",
            "[*] Pega ese comando en el sistema objetivo para instalar el agente.\n",
        ]

        for message in messages:
            print(message)

    def create_operation(self, name=None, adversary_id=None, agent_group="red"):
        """Crea una nueva operación en Caldera"""
        if not name:
            name = f"Operation_{generate_random_string(8)}"

        # Si no se proporciona un adversario, obtener el primero disponible
        if not adversary_id:
            adversaries = self.get_adversaries()
            if adversaries:
                adversary_id = adversaries[0]["adversary_id"]
            else:
                return None, "No hay adversarios disponibles"

        data = {
            "name": name,
            "adversary_id": adversary_id,
            "source": "API",
            "planner": "atomic",
            "state": "running",
            "autonomous": 1,
            "group": agent_group,
            "obfuscator": "plain-text",
        }

        response = requests.post(
            f"{self.base_url}/api/v2/operations",
            headers=self.headers,
            json=data,
            verify=False,
        )

        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"

    def get_operation_results(self, operation_id):
        """Obtiene los resultados de una operación"""
        response = requests.get(
            f"{self.base_url}/api/v2/operations/{operation_id}/report",
            headers=self.headers,
            verify=False,
        )
        return response.json()

    def wait_for_operation_completion(
        self, operation_id, timeout=300, check_interval=10
    ):
        """Espera a que una operación se complete"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/api/v2/operations/{operation_id}",
                headers=self.headers,
                verify=False,
            )

            if response.status_code == 200:
                operation = response.json()
                if operation["state"] == "finished":
                    return self.get_operation_results(operation_id)

            time.sleep(check_interval)

        return {"error": "Timeout waiting for operation completion"}

    def run_caldera_assessment(self, agent_group="red", adversary_name=None):
        # 1. Verificar agentes disponibles
        agents = self.get_agents()

        if not agents:
            return {"error": "No hay agentes disponibles para ejecutar la evaluación"}

        # 2. Seleccionar adversario
        adversary_id = None
        if adversary_name:
            adversaries = self.get_adversaries()
            for adversary in adversaries:
                if adversary["name"].lower() == adversary_name.lower():
                    adversary_id = adversary["adversary_id"]
                    break

            if not adversary_id:
                return {"error": f"Adversario '{adversary_name}' no encontrado"}

        # 3. Crear y ejecutar operación
        operation, error = self.create_operation(
            name=f"Assessment_{generate_random_string(8)}",
            adversary_id=adversary_id,
            agent_group=agent_group,
        )

        if error:
            return {"error": error}

        # 4. Esperar resultados
        operation_id = operation["id"]
        results = self.wait_for_operation_completion(operation_id)

        # 5. Procesar y devolver resultados
        return {
            "operation_id": operation_id,
            "adversary": operation.get("adversary", {}).get("name", "Unknown"),
            "start_time": operation.get("start", ""),
            "end_time": operation.get("finish", ""),
            "results": results,
        }
