import toml
from pathlib import Path
from .custom import RequestHeaders

module_path = Path(__file__).parent.parent.parent

request_headers = RequestHeaders.model_validate(toml.load(module_path / "./request.toml"))

__all__ = [ request_headers ]