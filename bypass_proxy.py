"""
Proxy reverso minimo que injeta o cookie de bypass do localtunnel
em todas as respostas, eliminando a tela de senha para o usuario.
"""
import asyncio
from aiohttp import web, ClientSession, WSMsgType

TARGET = "http://127.0.0.1:8501"
BYPASS_COOKIE = "bypass-tunnel-reminder=yt; Path=/; SameSite=None; Secure"

async def proxy_ws(request):
    ws_server = web.WebSocketResponse()
    await ws_server.prepare(request)

    async with ClientSession() as session:
        url = TARGET.replace("http", "ws") + request.path_qs
        async with session.ws_connect(url) as ws_client:
            async def forward(src, dst):
                async for msg in src:
                    if msg.type == WSMsgType.TEXT:
                        await dst.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await dst.send_bytes(msg.data)
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                        break

            await asyncio.gather(
                forward(ws_server, ws_client),
                forward(ws_client, ws_server),
            )
    return ws_server

async def proxy_http(request):
    async with ClientSession() as session:
        url = TARGET + request.path_qs
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in ("host", "connection")}
        async with session.request(
            request.method, url, headers=headers,
            data=await request.read(), allow_redirects=False
        ) as resp:
            body = await resp.read()
            out_headers = {k: v for k, v in resp.headers.items()
                           if k.lower() not in ("transfer-encoding", "content-encoding")}
            response = web.Response(body=body, status=resp.status, headers=out_headers)
            response.headers["bypass-tunnel-reminder"] = "yt"
            response.headers.add("Set-Cookie", BYPASS_COOKIE)
            return response

async def handler(request):
    if (request.headers.get("upgrade", "").lower() == "websocket" or
            request.headers.get("connection", "").lower() == "upgrade"):
        return await proxy_ws(request)
    return await proxy_http(request)

app = web.Application()
app.router.add_route("*", "/{path_info:.*}", handler)

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8502, access_log=None)
