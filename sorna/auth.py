import hashlib
import hmac
import io
from urllib.parse import urlsplit

from .request import Request


def sign(request):
    '''
    Calculates the signature of the given request and adds the Authorization HTTP header.
    It should be called at the very end of request preparation and before sending the request to the server.
    '''
    hash_type = request.config.hash_type
    hostname = urlsplit(request.config.endpoint).netloc
    body_hash = hashlib.new(hash_type, request.body).hexdigest()
    major_ver = request.config.version.split('.', 1)[0]

    sign_str = '{}\n/{}/{}\n{}\nhost:{}\ncontent-type:application/json\nx-sorna-version:{}\n{}'.format(
        request.method.upper(),
        major_ver, request.path,
        request.date.isoformat(),
        hostname,
        request.config.version,
        body_hash
    )
    sign_bytes = sign_str.encode()

    sign_key = hmac.new(request.config.secret_key.encode(),
                        request.date.strftime('%Y%m%d').encode(), hash_type).digest()
    sign_key = hmac.new(sign_key, hostname.encode(), hash_type).digest()

    signature = hmac.new(sign_key, sign_bytes, hash_type).hexdigest()
    request.headers['Authorization'] = 'Sorna signMethod=HMAC-{}, credential={}:{}'.format(
        request.config.hash_type.upper(),
        request.config.access_key,
        signature
    )


def authorize(echo_str):
    config = get_config()
    req = Request('GET', '/authorize', {
        'echo': echo_str,
    })
    return req.send()
