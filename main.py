from aiohttp import web
import json
import redis


class SimilarCurrencyException(Exception):
    pass

host = '127.0.0.1'
port = 5000

r = redis.Redis(host='localhost', port=6379, db=0)
r.set('USD', 76)
r.set('EUR', 85)

def get_from_db(cur_from, cur_to, amount):
    if cur_to != 'RUR' and cur_from != 'RUR':
        rub_from = r.get(cur_from)
        rub_to = r.get(cur_to)
        result = float(rub_from)*float(amount)/float(rub_to)
    elif cur_to == cur_from:
        raise SimilarCurrencyException
    elif cur_to == 'RUR':
        result = float(r.get(cur_from))*float(amount)
    elif cur_from == 'RUR':
        result = float(amount)/float(r.get(cur_to))
    return result




async def convert(request):
    try:
        cur_from = request.query['from']
        cur_to = request.query['to']
        amount = request.query['amount']
        result = get_from_db(cur_from, cur_to, amount)
        response_obj = {'status': 'success', 'result': str(result)}
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


routes = [web.get('/database', database), web.get('/convert', convert)]

app = web.Application()
app.add_routes(routes)


if __name__ == '__main__':
    web.run_app(app, host=host, port=port)


