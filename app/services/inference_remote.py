import requests
from requests.adapters import HTTPAdapter

from config import INFERENCE_REQUEST_TIMEOUT


class RemoteInferenceClient:
    """Cliente HTTP para o microserviço de inferência (monitoramento/deploy isolado)."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        adapter = HTTPAdapter(pool_connections=8, pool_maxsize=8)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def infer(self, image_file):
        image_file.stream.seek(0)
        raw = image_file.read()
        image_file.stream.seek(0)
        filename = image_file.filename or "image.jpg"
        content_type = image_file.content_type or "application/octet-stream"
        files = {"image": (filename, raw, content_type)}
        url = f"{self.base_url}/infer"
        try:
            response = self._session.post(
                url, files=files, timeout=INFERENCE_REQUEST_TIMEOUT
            )
        except requests.RequestException as exc:
            raise RuntimeError("Serviço de inferência indisponível") from exc

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get("error") or response.text or response.reason
            except ValueError:
                message = response.text or response.reason
            raise RuntimeError(message)

        data = response.json()
        if not data.get("success"):
            raise RuntimeError(data.get("error", "Falha na inferência"))
        return data
