from tusclient import client

import asyncio
from ai.backend.client.request import Request
from ai.backend.client.session import AsyncSession



loop = asyncio.get_event_loop()
async def request():
    """
    async with AsyncSession() as sess:

        rqst = Request(sess, 'POST', '/folders/mydata1/upload')
        async with rqst.fetch() as resp:
            print(await resp.text())
    
    """

    async with AsyncSession() as sess:

        
        rqst = Request(sess, "POST", "/folders/{}/create_upload_session".format("self.name"))
        session_url = 'http://127.0.0.1:8081/folders/{}/create_upload_session'.format("mydata1")
        request_url = 'http://127.0.0.1:8081/folders/{}/create_upload_session'.format("mydata1") # Should be changed, currently not clear directory path for file uploading at server vfolder routes '/_/tus/upload/{session}'
        
        tus_client = client.TusClient(request_url)
        tus_client.set_session_url(session_url)
        
        tus_client.set_headers(rqst.headers)
        print()
        fs = open("/Users/sergey/Documents/workspace/backend.ai_dev/client-py/src/ai/backend/client/func/user.py") # example file to upload
        uploader = tus_client.async_uploader(file_stream=fs)
        res = await uploader.upload()
    
def main():
    
    
        
    loop.run_until_complete(request())
    loop.close()


if __name__ == "__main__":
    main()