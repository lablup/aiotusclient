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

        headers = {'Host': '127.0.0.1:8081', 'User-Agent': 'Backend.AI Client for Python 20.03.0rc1.dev0', 'X-BackendAI-Domain': 'default', 'X-BackendAI-Version': 'v5.20191215', 
        'Date': '2020-07-28T01:01:22.205901+00:00', 'Authorization': 'BackendAI signMethod=HMAC-SHA256 \
        , credential=AKIAIOSFODNN7EXAMPLE:f7520bea59550400b1b67556aeeec22fa40e7f601c2245918a20de0200ce1348', 
        'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '396', 'Content-Type': 'multipart/form-data'}

        rqst = Request(sess, "POST", "/folders/{}/create_upload_session".format("mydata1"))
        request_url = 'http://127.0.0.1:8081/folders/{}/create_upload_session'.format("mydata1")
        tus_client = client.TusClient(request_url)
        tus_client.set_headers(headers)
        fs = open('/Users/sergey/Documents/workspace/backend.ai_dev/client-py/src/ai/backend/client/helper.py')
        uploader = tus_client.async_uploader(file_stream=fs)
        res = await uploader.upload()
        print(res)
    
def main():
    
    
        
    loop.run_until_complete(request())
    loop.close()


if __name__ == "__main__":
    main()