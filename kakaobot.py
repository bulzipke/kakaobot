import asyncio
import json
import os
import sqlite3

from aiohttp import web

FRIEND_STATUS_NORMAL = 0
FRIEND_STATUS_DELETE = 1
FRIEND_STATUS_LEAVE = 2

SQL_CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS {}({})'
SQL_INSERT = "INSERT INTO {} VALUES('{}', {})"
SQL_UPDATE = 'UPDATE {} SET {} WHERE {}'
SQL_SCAN = 'SELECT * FROM {}'

TABLE_FRIEND = 'friend'


class Bot:
    def __init__(self, port=8080, handle_message=None):
        # initialize web server
        self.app = web.Application()
        self.app.router.add_route('GET', '/keyboard', self._handle_keyboard)
        self.app.router.add_route('POST', '/friend', self._handle_friend)
        self.app.router.add_route('DELETE', '/friend/{user_key}', self._handle_friend)
        self.app.router.add_route('DELETE', '/chat_room/{user_key}', self._handle_friend)
        if handle_message is None:
            self.app.router.add_route('POST', '/message', self._handle_message)
        else:
            self.app.router.add_route('POST', '/message', handle_message)
        self._button_list = list()
        self._friend_list = list()

        # ready to graceful shutdown
        self.loop = asyncio.get_event_loop()
        self.handler = self.app.make_handler()
        self.future = self.loop.create_server(self.handler, '0.0.0.0', port)

        # initialize sqlite3
        dir_name = 'db'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        self.con = sqlite3.connect('{}/kakaobot.db'.format(dir_name))
        self.cursor = self.con.cursor()
        self.cursor.execute(SQL_CREATE_TABLE.format(TABLE_FRIEND, 'User text, Status int'))
        self._friend_list = dict(
            (friend[0], friend[1]) for friend in self.cursor.execute(SQL_SCAN.format(TABLE_FRIEND)).fetchall())

    async def _handle_keyboard(self, _):
        res = dict()

        if self._button_list:
            res['type'] = 'buttons'
            res['buttons'] = self._button_list
        else:
            res['type'] = 'text'

        return web.Response(body=json.dumps(res).encode('utf-8'),
                            content_type='application/json',
                            charset='utf-8')

    async def _handle_friend(self, request):
        if request.method == 'POST':
            req = await request.json()
            user_key = req.get('user_key', None)
            self._update_friend(user_key, FRIEND_STATUS_NORMAL)
        elif request.method == 'DELETE':
            user_key = request.match_info.get('user_key', None)
            if '/friend/' in request.path:
                self._update_friend(user_key, FRIEND_STATUS_DELETE)
            elif '/chat_room/' in request.path:
                self._update_friend(user_key, FRIEND_STATUS_LEAVE)

        return web.Response()

    async def _handle_message(self, request):
        req = await request.json()

        res = dict()
        res['message'] = {
            'text': req['content']
        }

        return web.Response(body=json.dumps(res).encode('utf-8'),
                            content_type='application/json',
                            charset='utf-8')

    def _update_friend(self, user_key, status):
        if user_key in self._friend_list:
            value = 'Status={}'.format(status)
            condition = 'User={}'.format("'{}'".format(user_key))
            query = SQL_UPDATE.format(TABLE_FRIEND, value, condition)
        else:
            query = SQL_INSERT.format(TABLE_FRIEND, user_key, FRIEND_STATUS_NORMAL)
        self.con.execute(query)
        self._friend_list[user_key] = status

    def add_button(self, name):
        self._button_list.append(name)

    def start(self):
        try:
            server = self.loop.run_until_complete(self.future)
        except OSError as e:
            print(e)
            return

        print('Kakaobot is running on', server.sockets[0].getsockname())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            self.loop.run_until_complete(server.wait_closed())
            self.loop.run_until_complete(self.app.shutdown())
            self.loop.run_until_complete(self.handler.finish_connections(60.0))
            self.loop.run_until_complete(self.app.cleanup())
            self.con.commit()
            self.con.close()
        self.loop.close()
