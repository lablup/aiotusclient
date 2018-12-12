import asyncio
import aiohttp

from . import register_command
from .pretty import print_info
from ..request import Request
from ..session import AsyncSession
from ..compat import current_loop


class WSProxy:
    __slots__ = (
        'conn', 'down_conn', 'upstream_buffer', 'upstream_buffer_task',
        'reader', 'writer', 'api_session', 'path',
    )
    BUFFER_SIZE = 8192

    def __init__(self, api_session: AsyncSession,
                 session_id: str,
                 protocol: str,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.api_session = api_session
        self.path = f"/stream/kernel/{session_id}/{protocol}proxy"
        self.reader = reader
        self.writer = writer

    async def run(self):
        api_rqst = Request(
            self.api_session, "GET", self.path, b'',
            content_type="application/json")
        async with api_rqst.connect_websocket() as ws:
            async def up():
                try:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.ERROR:
                            await self.write_error_and_close()
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSE:
                            if msg.data != aiohttp.WSCloseCode.OK:
                                await self.write_error_and_close()
                            break
                        elif msg.type == aiohttp.WSMsgType.BINARY:
                            self.writer.write(msg.data)
                            await self.writer.drain()
                finally:
                    self.writer.close()
                    await ws.close()
            task = asyncio.ensure_future(up())
            while True:
                try:
                    chunk = await self.reader.read(self.BUFFER_SIZE)
                    if not chunk:
                        break
                    await ws.send_bytes(chunk)
                except GeneratorExit:
                    break

        await self.close()

    async def close(self):
        await self.writer.drain()
        self.writer.close()
        await self.writer.wait_closed()

    async def write_error_and_close(self):
        rsp = 'HTTP/1.1 503 Service Unavailable\n' \
            'Connection: Closed\n' \
            '\n' \
            'Service Unavailable\n'
        self.writer.write(rsp.encode())
        await self.close()


class ProxyRunner:
    __slots__ = (
        'session_id', 'app_name',
        'protocol', 'host', 'port',
        'api_session', 'local_server', 'loop',
    )

    def __init__(self, session_id, name, protocol, host, port, *, loop=None):
        self.session_id = session_id
        self.app_name = name
        self.protocol = protocol
        self.host = host
        self.port = port
        self.api_session = None
        self.local_server = None
        self.loop = loop if loop else current_loop()

    async def handle_connection(self, reader, writer):
        p = WSProxy(self.api_session, self.session_id,
                    self.protocol, reader, writer)
        await p.run()

    async def ready(self):
        self.api_session = AsyncSession()

        self.local_server = await asyncio.start_server(
            self.handle_connection, self.host, self.port,
            loop=self.loop)

        print_info(
            "A local proxy to the application \"{0}\" ".format(self.app_name) +
            "provided by the session \"{0}\" ".format(self.session_id) +
            "is available at: {0}://{1}:{2}"
            .format(self.protocol, self.host, self.port)
        )

    async def close(self):
        self.local_server.close()
        await self.local_server.wait_closed()
        await self.api_session.close()


@register_command
def app(args):
    """
    Run a local proxy to a service provided by Backend.AI
    compute sessions.

    The type of proxy depends on the app definition: plain TCP or HTTP.
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # TODO: generalize protocol using service ports metadata
    runner = ProxyRunner(args.session_id, args.app,
                         'http', args.bind, args.port,
                         loop=loop)
    loop.run_until_complete(runner.ready())
    try:
        loop.run_forever()
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        print_info("Shutting down....")
        try:
            loop.run_until_complete(runner.close())
        finally:
            print_info("Done")
            loop.close()


app.add_argument('session_id', type=str, metavar='SESSID',
                 help='The compute session ID.')
app.add_argument('app', type=str,
                 help='The name of service provided by the given session.')
app.add_argument('--bind', type=str, default='127.0.0.1',
                   help='The IP/host address to bind this proxy.')
app.add_argument('-p', '--port', type=int, default=8080,
                   help='The port number to listen user connections.')
