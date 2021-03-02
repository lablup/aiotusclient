import asyncio
from typing import Optional

from tqdm import tqdm

from .baseuploader import BaseUploader
from .exceptions import TusCommunicationError, TusUploadFailed
from .request import AsyncTusRequest


def _verify_upload(request: AsyncTusRequest):
    if request.status_code == 204:
        return True
    else:
        raise TusUploadFailed("", request.status_code, request.response_content)


class AsyncUploader(BaseUploader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def upload(self, stop_at: Optional[int] = None):
        """
        Perform file upload.

        Performs continous upload of chunks of the file. The size uploaded at each cycle is
        the value of the attribute 'chunk_size'.

        :Args:
            - stop_at (Optional[int]):
                Determines at what offset value the upload should stop. If not specified this
                defaults to the file size.
        """
        self.stop_at = stop_at or self.get_file_size()

        with tqdm(
            total=self.get_file_size(), unit="bytes", unit_scale=True, unit_divisor=1024
        ) as pbar:

            while self.offset < self.stop_at:
                await self.upload_chunk()
                pbar.update(self.chunk_size)

    async def upload_chunk(self):
        """
        Upload chunk of file.
        """
        await self._do_request()
        self.offset = int(self.request.response_headers.get("upload-offset"))

    async def _do_request(self):
        self.request = AsyncTusRequest(self)
        try:
            await self.request.perform()
            _verify_upload(self.request)
        except TusUploadFailed as error:
            await self._retry_or_cry(error)

    async def _retry_or_cry(self, error):
        print("Error ", error)
        print("Retries ", self.retries, self._retried)
        if self.retries > self._retried:
            await asyncio.sleep(self.retry_delay)
            self._retried += 1
            try:
                print("Awaiting   ....")
                self.offset = await self.get_offset()
            except TusCommunicationError as err:
                await self._retry_or_cry(err)
            else:
                await self._do_request()
        else:
            print("Error ", error)
            raise error
