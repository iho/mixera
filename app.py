import json
import os

import psycopg2

import aiopg
import asyncio
import db
from aiohttp.web import Application, MsgType, Response, WebSocketResponse

WS_FILE = os.path.join(os.path.dirname(__file__), 'websocket.html')

async def endpointhandler(request):
    pool = request.app['db_pool']
    data = await request.json()
    if data['type'] == 'get_user_list':
        response = await db.get_users(pool)
        print(response)
    elif data['type'] == 'get_online_user_list':
        response = []
        for ws in request.app['sockets']:
            user = getattr(ws, 'user')
            if user:
                user['status'] = 'online'
                response.append(user)
        print(response)
    return Response(text=json.dumps(response))


async def wshandler(request):
    pool = request.app['db_pool']
    resp = WebSocketResponse()
    ok, protocol = resp.can_start(request)
    if not ok:
        with open(WS_FILE, 'rb') as fp:
            return Response(body=fp.read(), content_type='text/html')

    await resp.prepare(request)
    print('Someone joined.')
    for ws in request.app['sockets']:
        ws.send_str('Someone joined')
    request.app['sockets'].append(resp)

    while True:
        msg = await resp.receive()
        try:
            data = json.loads(msg.data)
        except:
            data = ''

        def broadcast(message):
            message = json.dumps(message)
            for ws in request.app['sockets']:
                if ws is not resp:
                    ws.send_str(msg.data)

        def reply(message):
            message = json.dumps(message)
            resp.send_str(message)

        if msg.tp == MsgType.text:
            if isinstance(data, dict) and data.get('type'):
                if data['type'] == 'message':
                    print(resp.user)
                     
                    await db.create_message(pool, data, resp.user['id'] )

                    response = {'type': 'message', 'status': None}
                    
                    user_to_id = data.get('to')
                    if user_to_id:
                        for ws in request.app['sockets']:
                            user = getattr(ws, 'user')
                            if user['id'] == user_to_id:
                                response['status'] = 'online'
                    reply(response)
                    data['from'] = resp.user['id']
                    reply(data)
                    broadcast(data)

                elif data['type'] == 'login':
                    res = {'type': 'login',  'logined': False}
                    print(data)
                    user = await db.check_password(pool, data)
                    print(user)
                    if user:
                        res['logined'] = True
                        del user['password'] 
                        resp.user = user
                    reply(res)

                elif data['type'] == 'register':
                    user = await db.create_user(pool, data)
                    res = {'type': 'register',  'logined': False}
                    if user:
                        res['logined'] = True
                        user.update(data)
                        del user['password'] 
                        resp.user = user
                    reply(res)

                else:
                    reply({'error': 'Message type is incorect'})
            else:
                reply({'error': 'Cannot parse request message'})
        else:
            break

    request.app['sockets'].remove(resp)
    print('Someone disconnected.')
    for ws in request.app['sockets']:
        ws.send_str('Someone disconnected.')
    return resp


async def init(loop):
    app = Application(loop=loop)
    app['sockets'] = []
    app.router.add_route('GET', '/', wshandler)
    app.router.add_route('POST', '/endpoint', endpointhandler)
    app.router.add_static('/static', './static')
    dsn = 'dbname=aiopg_db user=aiopg_user password=password host=127.0.0.1'

    pool = await aiopg.create_pool(dsn,
                                   cursor_factory=psycopg2.extras.RealDictCursor,
                                   echo=True)
    app['db_pool'] = pool

    asyncio.ensure_future(db.create_tables(pool))

    handler = app.make_handler()
    srv = await loop.create_server(handler, '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return app, srv, handler


async def finish(app, srv, handler):
    for ws in app['sockets']:
        ws.close()
    app['sockets'].clear()
    await asyncio.sleep(0.1)
    srv.close()
    await handler.finish_connections()
    await srv.wait_closed()


loop = asyncio.get_event_loop()
app, srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(finish(app, srv, handler))
