from aiohttp import web
import json


async def convert(request):
    try:
        response_obj = {'status': 'success'}

        cur_from = request.query['from']
        cur_to = request.query['to']
        amount = request.query['amount']
        print(cur_from, cur_to, amount)
        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)


async def database(request):
    try:
        response_obj = {'status': 'success'}
        merge = request.query['merge']
        if merge == 0:
            pass
        elif merge == 1:
            pass

        return web.Response(text=json.dumps(response_obj), status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.Response(text=json.dumps(response_obj), status=500)
app = web.Application()
#app.router.add_get('/', handle)
routes = [web.get('/database', database), web.get('/convert', convert)]
app.add_routes(routes)

host = '127.0.0.1'
port = 5000

if __name__ == '__main__':
    web.run_app(app, host=host, port=port)


