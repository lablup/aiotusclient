from datetime import datetime
import uuid

from dateutil.tz import tzutc
import pytest

from ai.backend.client import Session, AsyncSession
from ai.backend.client.auth import generate_signature
from ai.backend.client.request import Request
from ai.backend.client.exceptions import BackendAPIError


@pytest.mark.integration
class TestAuth:

    def test_auth(self):
        random_msg = uuid.uuid4().hex
        with Session() as sess:
            request = Request(sess, 'GET', '/auth')
            request.set_json({
                'echo': random_msg,
            })
            with request.fetch() as resp:
                assert resp.status == 200
                data = resp.json()
                assert data['authorized'] == 'yes'
                assert data['echo'] == random_msg

    def test_auth_missing_signature(self, monkeypatch):
        random_msg = uuid.uuid4().hex
        with Session() as sess:
            rqst = Request(sess, 'GET', '/auth')
            rqst.set_json({'echo': random_msg})
            # let it bypass actual signing
            from ai.backend.client import request
            noop_sign = lambda *args, **kwargs: ({}, None)
            monkeypatch.setattr(request, 'generate_signature', noop_sign)
            with pytest.raises(BackendAPIError) as e:
                with rqst.fetch():
                    pass
            assert e.value.status == 401

    def test_auth_malformed(self):
        with Session() as sess:
            request = Request(sess, 'GET', '/auth')
            request.set_content(
                b'<this is not json>',
                content_type='application/json',
            )
            with pytest.raises(BackendAPIError) as e:
                with request.fetch():
                    pass
            assert e.value.status == 400

    def test_auth_missing_body(self):
        with Session() as sess:
            request = Request(sess, 'GET', '/auth')
            with pytest.raises(BackendAPIError) as e:
                with request.fetch():
                    pass
            assert e.value.status == 400

    @pytest.mark.asyncio
    async def test_async_auth(self):
        random_msg = uuid.uuid4().hex
        async with AsyncSession() as sess:
            request = Request(sess, 'GET', '/auth')
            request.set_json({
                'echo': random_msg,
            })
            async with request.fetch() as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data['authorized'] == 'yes'
                assert data['echo'] == random_msg


def test_generate_signature(defconfig):
    kwargs = dict(
        method='GET',
        version=defconfig.version,
        endpoint=defconfig.endpoint,
        date=datetime.now(tzutc()),
        rel_url='/path/to/api/',
        content_type='plain/text',
        content=b'"test data"',
        access_key=defconfig.access_key,
        secret_key=defconfig.secret_key,
        hash_type='md5'
    )
    headers, signature = generate_signature(**kwargs)

    assert kwargs['hash_type'].upper() in headers['Authorization']
    assert kwargs['access_key'] in headers['Authorization']
    assert signature in headers['Authorization']
