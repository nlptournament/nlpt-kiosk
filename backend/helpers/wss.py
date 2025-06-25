import asyncio
import json
from websockets.asyncio.server import broadcast, serve
from multiprocessing import Process
from helpers.asyncprocessqueue import AsyncProcessQueue
from elements import Setting

ws_process, conn_process = (None, None)
com_tx_queue = AsyncProcessQueue()
com_rx_queue = AsyncProcessQueue()


def _websocket_process(rx_queue, tx_queue):
    CONNECTIONS = set()

    async def _rx_handler(websocket):
        addr, port = websocket.remote_address
        try:
            CONNECTIONS.add(websocket)
            rx_queue.put({'what': 'add', 'ws': f'{addr}:{port}'})
            async for msg in websocket:
                rx_queue.put({'what': 'rec', 'ws': f'{addr}:{port}', 'msg': msg})
        finally:
            CONNECTIONS.remove(websocket)
            rx_queue.put({'what': 'del', 'ws': f'{addr}:{port}'})

    @asyncio.coroutine
    def _tx_handler():
        while True:
            msg = yield from tx_queue.coro_get()
            if 'target' not in msg or 'msg' not in msg:
                continue
            if isinstance(msg['target'], str) and msg['target'] == 'all':
                broadcast(CONNECTIONS, msg['msg'])
            elif not isinstance(msg['target'], list) or len(msg['target']) == 0:
                continue
            else:
                targets = set()
                for c in CONNECTIONS:
                    addr, port = c.remote_address
                    if f'{addr}:{port}' in msg['target']:
                        targets.add(c)
                broadcast(targets, msg['msg'])

    async def _main():
        txh = asyncio.create_task(_tx_handler())
        async with serve(_rx_handler, '0.0.0.0', Setting.value('wss_port')) as server:
            await server.serve_forever()
        await txh

    asyncio.run(_main())


def _connection_process(rx_queue, tx_queue):
    from elements import Session
    CLIENTS = dict()

    while True:
        msg = rx_queue.get()
        if 'what' not in msg:
            continue

        if msg['what'] == 'add' and 'ws' in msg:
            if msg['ws'] not in CLIENTS:
                CLIENTS[msg['ws']] = dict()

        elif msg['what'] == 'del' and 'ws' in msg:
            CLIENTS.pop(msg['ws'], None)

        elif msg['what'] == 'rec' and 'ws' in msg and 'msg' in msg and msg['ws'] in CLIENTS:
            msg['msg'] = json.loads(msg['msg'])
            if 'session' in msg['msg']:
                s = Session.get(msg['msg']['session'])
                if s['_id'] is None:
                    continue
                if s['complete']:
                    CLIENTS[msg['ws']]['user_id'] = s['user_id']
                    CLIENTS[msg['ws']]['admin'] = s.admin()

        elif msg['what'] == 'send' and 'target' in msg and 'msg' in msg:
            # all connected websockets regardless of admin-interface users or kiosks
            if msg['target'] == 'all':
                tx_queue.put({'target': 'all', 'msg': msg['msg']})
            # all logged in admin-interface users
            elif msg['target'] == 'users':
                t = list()
                for c, p in CLIENTS.items():
                    if 'user_id' in p:
                        t.append(c)
                if len(t) > 0:
                    tx_queue.put({'target': t, 'msg': msg['msg']})
            # all logged in admins
            elif msg['target'] == 'admins':
                t = list()
                for c, p in CLIENTS.items():
                    if 'admin' in p and p['admin']:
                        t.append(c)
                if len(t) > 0:
                    tx_queue.put({'target': t, 'msg': msg['msg']})
            # logged in owner and all admins
            elif msg['target'] == 'owner' and 'owner_id' in msg:
                t = list()
                for c, p in CLIENTS.items():
                    if 'user_id' in p and (p['admin'] or p['user_id'] == msg['owner_id']):
                        t.append(c)
                if len(t) > 0:
                    tx_queue.put({'target': t, 'msg': msg['msg']})


def start_server():
    global ws_process, conn_process
    if ws_process is None:
        ws_process = Process(target=_websocket_process, args=(com_rx_queue, com_tx_queue, ), daemon=True)
        ws_process.start()
    if conn_process is None:
        conn_process = Process(target=_connection_process, args=(com_rx_queue, com_tx_queue), daemon=True)
        conn_process.start()


def transmit_kiosk_update(kiosk):
    result = {'kiosk': kiosk.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'all', 'msg': json.dumps(result)})


def transmit_kiosk_delete(kiosk):
    result = {'kiosk': kiosk.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'all', 'msg': json.dumps(result)})


def transmit_timeline_update(timeline):
    result = {'timeline': timeline.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_timeline_delete(timeline):
    result = {'timeline': timeline.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_screen_update(screen):
    result = {'screen': screen.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_screen_delete(screen):
    result = {'screen': screen.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_preset_update(preset):
    result = {'preset': preset.json(), 'content': 'update'}
    if preset['common']:
        com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})
    else:
        com_rx_queue.put({'what': 'send', 'target': 'owner', 'owner_id': preset['user_id'], 'msg': json.dumps(result)})


def transmit_preset_delete(preset):
    result = {'preset': preset.json(), 'content': 'delete'}
    if preset['common']:
        com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})
    else:
        com_rx_queue.put({'what': 'send', 'target': 'owner', 'owner_id': preset['user_id'], 'msg': json.dumps(result)})


def transmit_timelinetemplate_update(timelinetemplate):
    result = {'timelinetemplate': timelinetemplate.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_timelinetemplate_delete(timelinetemplate):
    result = {'timelinetemplate': timelinetemplate.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_user_update(user):
    result = {'user': user.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_user_delete(user):
    result = {'user': user.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_media_update(media):
    result = {'media': media.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'owner', 'owner_id': media['user_id'], 'msg': json.dumps(result)})


def transmit_media_delete(media):
    result = {'media': media.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'users', 'msg': json.dumps(result)})


def transmit_challonge_update(chal, what):
    result = {f'challonge_{what}': chal.json(), 'content': 'update'}
    com_rx_queue.put({'what': 'send', 'target': 'kiosks', 'msg': json.dumps(result)})


def transmit_challonge_delete(chal, what):
    result = {f'challonge_{what}': chal.json(), 'content': 'delete'}
    com_rx_queue.put({'what': 'send', 'target': 'kiosks', 'msg': json.dumps(result)})
