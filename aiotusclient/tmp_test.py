from typing import Dict

from .uploader import AsyncUploader


class TusClient:
    """
    Object representation of Tus client for the Backend.AI.

    :Attributes:
        - headers (dict):
            This can be used to set the server specific headers. These headers
            would be sent along with every request made by the cleint to the
            server. This may be used to set
            authentication headers.
            These headers should not include headers required by tus
            protocol. If not set this defaults to an empty dictionary.

    :Constructor Args:
        - headers (Optiional[dict])
    """

    def __init__(self, headers: Dict[str, str] = None):
        self.headers = headers if headers else {}

    def async_uploader(self, *args, **kwargs) -> AsyncUploader:
        kwargs["client"] = self
        return AsyncUploader(*args, **kwargs)
