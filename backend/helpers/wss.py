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
            rx_queue.put({'what': 'del', 'ws': f'{addr}:{port}'})

    @asyncio.coroutine
    def _tx_handler():
        while True:
            msg = yield from tx_queue.coro_get()
            if 'target' not in msg:
                continue
            if msg['target'] == 'all':
                broadcast(CONNECTIONS, msg['msg'])

    async def _main():
        txh = asyncio.create_task(_tx_handler())
        async with serve(_rx_handler, '0.0.0.0', Setting.value('wss_port')) as server:
            await server.serve_forever()
        await txh

    asyncio.run(_main())


def _connection_process(rx_queue, tx_queue):
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
        elif msg['what'] == 'rec' and 'ws' in msg:
            pass
        elif msg['what'] == 'send' and msg['target'] == 'all':
            tx_queue.put({'target': 'all', 'msg': msg['msg']})


def start_server():
    global ws_process, conn_process, com_queue
    if ws_process is None:
        ws_process = Process(target=_websocket_process, args=(com_rx_queue, com_tx_queue, ))
        ws_process.start()
    if conn_process is None:
        conn_process = Process(target=_connection_process, args=(com_rx_queue, com_tx_queue))
        conn_process.start()


def transmit_timeline_update(timeline):
    global com_tx_queue
    result = {'timeline': timeline.json()}
    com_rx_queue.put({'what': 'send', 'target': 'all', 'msg': json.dumps(result)})
