import requests
from config import BASE_URL, logger


class DeadlockAPIClient:
    """Cliente HTTP reutilizável com timeout e tratamento de erros."""

    def __init__(self, base_url: str = BASE_URL, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint: str, params: dict = None) -> list | dict:
        """Executa uma requisição GET com logging e controle de falhas."""
        url = f"{self.base_url}{endpoint}"
        logger.info("Requisitando endpoint: %s", endpoint)

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error("Erro HTTP ao acessar %s: %s", url, http_err)
            raise
        except requests.exceptions.RequestException as req_err:
            logger.error("Erro de conexão com a API em %s: %s", url, req_err)
            raise

