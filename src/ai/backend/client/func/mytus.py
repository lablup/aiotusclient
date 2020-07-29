from tusclient import client

import asyncio
from ai.backend.client.request import Request
from ai.backend.client.session import AsyncSession


from datetime import datetime
from dateutil.tz import tzutc
from ai.backend.client.auth import generate_signature

loop = asyncio.get_event_loop()
async def request():
    """
    async with AsyncSession() as sess:

        rqst = Request(sess, 'POST', '/folders/mydata1/upload')
        async with rqst.fetch() as resp:
            print(await resp.text())
    
    """

    async with AsyncSession() as sess:

        

        rqst = Request(sess, "POST", "/folders/{}/create_upload_session".format("mydata1"))
        
        date = datetime.now(tzutc())

        rqst.content_type = "multipart/form-data"
        hdrs, _ = generate_signature(
            method=rqst.method,
            version=rqst.api_version,
            endpoint=rqst.config.endpoint,
            date=date,
            rel_url="/folders/mydata1/create_upload_session?path='http://127.0.0.1:8081/folders/mydata1/create_upload_session'&size=1024",
            content_type=rqst.content_type,
            access_key=sess.config.access_key,
            secret_key=sess.config.secret_key,
            hash_type=sess.config.hash_type
        )
        
        rqst.headers["Date"] = date.isoformat()
        rqst.headers["content-type"] = "multipart/form-data"


        rqst.headers.update(hdrs)
        print(rqst.path)

        session_url = 'http://127.0.0.1:8081/folders/{}/create_upload_session'.format("mydata1")
        request_url = 'http://127.0.0.1:8081/folders/{}/create_upload_session'.format("mydata1") # Should be changed, currently not clear directory path for file uploading at server vfolder routes '/_/tus/upload/{session}'
        
        tus_client = client.TusClient(request_url)
        tus_client.set_session_url(session_url)
        
        tus_client.set_headers(rqst.headers)
        print(rqst.headers)
        print()
        fs = open("/Users/sergey/Documents/workspace/backend.ai_dev/client-py/src/ai/backend/client/func/user.py") # example file to upload
        uploader = tus_client.async_uploader(file_stream=fs)
        res = await uploader.upload()
    
def main():
    
    
        
    loop.run_until_complete(request())
    loop.close()


if __name__ == "__main__":
    main()