import requests
import logging
import json
import os
from auth.auth import Auth
from utils.logger import configure_logger

# Obter o logger configurado
logger = configure_logger()


class Listing:
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

    def get_ticket_list(self):
        url = "https://api.desk.ms/ChamadosSuporte/lista"
        parameters = json.dumps(
            {
                "Pesquisa": "",
                "Tatual": "",
                "Ativo": "NaFila",
                "StatusSLA": "N",
                "Colunas": {
                    "Chave": "on",
                    "CodChamado": "on",
                    "NomePrioridade": "on",
                    "DataCriacao": "on",
                    "HoraCriacao": "on",
                    "DataFinalizacao": "on",
                    "HoraFinalizacao": "on",
                    "DataAlteracao": "on",
                    "HoraAlteracao": "on",
                    "NomeStatus": "on",
                    "Assunto": "on",
                    "Descricao": "on",
                    "ChaveUsuario": "on",
                    "NomeUsuario": "on",
                    "SobrenomeUsuario": "on",
                    "NomeOperador": "on",
                    "SobrenomeOperador": "on",
                    "TotalAcoes": "on",
                    "TotalAnexos": "on",
                    "Sla": "on",
                    "CodGrupo": "on",
                    "NomeGrupo": "on",
                    "CodSolicitacao": "on",
                    "CodSubCategoria": "on",
                    "CodTipoOcorrencia": "on",
                    "CodCategoriaTipo": "on",
                    "CodPrioridadeAtual": "on",
                    "CodStatusAtual": "on"
                },
                "Ordem": [{"Coluna": "Chave", "Direcao": "true"}]
            }
        )
        try:
            response_data = self.make_api_request(url, parameters)

            if response_data:
                logger.info(f"{os.path.basename(__file__)}: Requisição bem-sucedida.")
                return response_data
            else:
                logger.warning(
                    f"{os.path.basename(__file__)}: Falha ao obter a lista de tickets."
                )
                return None

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logger.warning(
                    f"{os.path.basename(__file__)}: Token expirado. Atualizando token e tentando novamente..."
                )
                self.refresh_token()  # Tenta atualizar o token
                return None  # Retorna None após a falha
            else:
                logger.error(f"{os.path.basename(__file__)}: HTTPError: {http_err}")
                raise  # Re-levanta o erro
                return None
