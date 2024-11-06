import requests
import json
import os
from datetime import datetime
from utils.logger import configure_logger

# Obter o logger configurado
logger = configure_logger()


class Auth:
    def __init__(self, url="https://api.desk.ms/Login/autenticar"):
        self.__token = ""
        self.url = url

    def token(self) -> str | None:
        # Usar variáveis de ambiente para obter as credenciais
        authorization = os.getenv(
            "AUTHORIZATION"
        )  # Certifique-se de que as variáveis de ambiente estão configuradas corretamente
        public_key = os.getenv("PUBLICKEY")

        if not authorization or not public_key:
            logger.warning(
                f"{os.path.basename(__file__)}: As variáveis de ambiente AUTHORIZATION ou PUBLICKEY estão faltando."
            )
            return None

        header = {"Authorization": authorization, "content-type": "application/json"}
        params = json.dumps({"PublicKey": public_key})

        try:
            logger.info(
                f"Enviando requisição de autenticação para {self.url}..."
            )  # Log de início
            with requests.Session() as session:
                response = session.post(self.url, headers=header, data=params)
                response.raise_for_status()

                self.__token = response.json()
                os.environ["TOKEN"] = self.__token

                logger.info(
                    f"Token adquirido com sucesso: {self.__token}"
                )  # Log de sucesso
                return self.__token
        except requests.RequestException as e:
            logger.error(f"Falha ao obter o token. Erro: {e}")
            return None
