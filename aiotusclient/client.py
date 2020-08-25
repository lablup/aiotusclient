from typing import Dict

from .uploader import Uploader, AsyncUploader


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

    def uploader(self, *args, **kwargs) -> Uploader:
        """
        Return uploader instance pointing at current client instance.

        Return uplaoder instance with which you can control the upload of a specific
        file. The current instance of the tus client is passed to the uploader on creation.

        :Args:
            see tusclient.uploader.Uploader for required and optional arguments.
        """
        kwargs['client'] = self
        return Uploader(*args, **kwargs)

    def async_uploader(self, *args, **kwargs) -> AsyncUploader:
        kwargs['client'] = self
        return AsyncUploader(*args, **kwargs)
