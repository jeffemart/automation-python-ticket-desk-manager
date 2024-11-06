import requests
import logging
import json
import os
from auth.auth import Auth
from utils.logger import configure_logger

# Obter o logger configurado
logger = configure_logger()


class SubcategoryListing:
    def __init__(self):
        # Verifica se a variável de ambiente 'TOKEN' existe e a usa
        self.token = os.getenv("TOKEN")
        if not self.token:
            logger.warning(
                f"{os.path.basename(__file__)}: Token não encontrado nas variáveis de ambiente."
            )
            # Tenta obter o token se não houver
            auth = Auth()
            self.token = auth.token()

        self.header = {"Authorization": f"{self.token}"}
        self.refresh_token()

    def refresh_token(self):
        # Atualiza o header com o novo token se necessário
        if not self.token:
            logger.warning(f"{os.path.basename(__file__)}: Token não definido.")
        else:
            self.header = {"Authorization": f"{self.token}"}

    def refresh_new_token(self):
        # Tenta obter um novo token se necessário
        auth_instance = Auth()
        new_token = auth_instance.token()
        if new_token:
            logger.info(
                f"{os.path.basename(__file__)}: Token atualizado com sucesso: {new_token}"
            )
            self.token = new_token
            self.header = {"Authorization": f"{self.token}"}
        else:
            logger.warning(f"{os.path.basename(__file__)}: Falha ao obter o token.")

    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            response_data = response.json()

            logger.info(
                f"{os.path.basename(__file__)}: API Request to {url} with params: {params}"
            )

            if response_data != {"erro": "Token expirado ou não existe"}:
                return response_data["root"]
            else:
                logger.warning(
                    f"{os.path.basename(__file__)}: Token expirado ou não disponível."
                )
                self.refresh_new_token()  # Atualiza o token
                return None

        except requests.RequestException as e:
            if e.response and e.response.status_code == 401:  # Verifica erro 401
                logger.warning(
                    f"{os.path.basename(__file__)}: Token expirado. Atualizando token e tentando novamente..."
                )
                self.refresh_new_token()  # Atualiza o token e tenta novamente
                return self.make_api_request(
                    url, params
                )  # Recursivamente tenta novamente a requisição
            else:
                logger.error(
                    f"{os.path.basename(__file__)}: Error in API request: {e}"
                )
                raise  # Rethrow the exception after logger
            raise

    def get_subcategory_list(self):
        url = "https://api.desk.ms/SubCategorias/lista"
        parameters = {
            "Pesquisa": "",
            "Ativo": "S",
            "Ordem": [{"Coluna": "SubCategoria", "Direcao": "true"}],
        }

        try:
            response_data = self.make_api_request(url, parameters)

            if response_data:
                logger.info("Subcategory list obtained successfully")

                # Process the response_data as needed

                # Save response_data to a JSON file
                self.save_to_json(response_data, "subcategory_list.json")

                return response_data
            else:
                logger.warning("Failed to obtain subcategory list.")
                return None

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logger.warning("Token expired. Refreshing token and retrying...")
                # Adicione a lógica para atualizar o token, se necessário
                return (
                    self.get_subcategory_list()
                )  # Tentar novamente após a atualização do token
            else:
                logger.error("HTTPError: %s", http_err)
                raise  # Rethrow the exception after logger
        except Exception as e:
            logger.error("Error: %s", e)
            raise  # Rethrow the exception after logger

    def save_to_json(self, data, filename):
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
