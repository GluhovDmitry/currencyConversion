'''

This is REST API for currency conversion. File conversion is "get" handler, db_update - "post".

'''

from aiohttp import web
from conversion import *
from db_update import *


async def init():
    routes = [web.post('/database', database_update_handler), web.get('/conversion', convert_handler)]
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 5000
    application = init()
    web.run_app(application, host=host, port=port)
