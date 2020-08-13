from typing import Dict, Optional
from multidict import CIMultiDict
from .uploader import Uploader, AsyncUploader


class TusClient:
    """
    Object representation of Tus client for the Backend.AI.

    :Attributes:
        - url (str):
            represents the tus server's create extension url. On instantiation
            this argument must be passed to the constructor.
        - headers (dict):
            This can be used to set the server specific headers. These headers
            would be sent along with every request made by the cleint to the
            server. This may be used to set
            authentication headers.
            These headers should not include headers required by tus
            protocol. If not set this defaults to an empty dictionary.

    :Constructor Args:
        - url (str)
        - headers (Optiional[dict])
    """

    def __init__(self, session_create_url: str, session_upload_url: str,
                 headers: Optional[CIMultiDict[str]],
                 params: Optional[Dict[str, object]] = None):
        self.url = session_create_url
        self.session_create_url = session_create_url
        self.session_upload_url = session_upload_url
        self.headers = headers
        self.params = params or {}

    def set_headers(self, headers: Dict[str, str]):
        """
        Set tus client headers.

        Update and/or set new headers that would be sent along with every request made
        to the server.

        :Args:
            - headers (dict):
                key, value pairs of the headers to be set. This argument is required.
        """
        # self.headers.update(headers)

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