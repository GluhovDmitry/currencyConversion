# curl -i -X GET http://localhost:5000/convert?from=RUR&to=USD&amount=40
# curl -i -X POST -H 'Content-Type: application/json' -d '{'EUR':89, 'USD':76}' http://localhost:5000/database/merge=1


from aiohttp import web
import redis
import json


class SimilarCurrencyException(Exception):
    pass


class EmptyDataException(Exception):
    pass


class InvalidMergeValueException(Exception):
    pass


host = '127.0.0.1'
port = 5000

r = redis.Redis(host='localhost', port=6379, db=0)


def get_conversion(cur_from, cur_to, amount):
    result = 0.0
    if cur_to != 'RUR' and cur_from != 'RUR':
        rub_from = r.get(cur_from)
        rub_to = r.get(cur_to)
        result = float(rub_from) * float(amount) / float(rub_to)
    elif cur_to == cur_from:
        raise SimilarCurrencyException
    elif cur_to == 'RUR':
        result = float(r.get(cur_from)) * float(amount)
    elif cur_from == 'RUR':
        result = float(amount) / float(r.get(cur_to))
    return result


async def convert_handler(request):
    try:
        cur_from = request.query['from']
        cur_to = request.query['to']
        amount = request.query['amount']
        result = get_conversion(cur_from, cur_to, amount)
        response_obj = {'status': 'success', 'result': str(round(result, 2))}
        return web.json_response(response_obj, status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def database_update_handler(request):
    try:
        is_merge = int(request.query['merge'])
        data = await request.json()
        curs, values = [], []
        if type(data['cur']) == list and type(data['value']) == list:
            curs = data['cur']
            values = data['value']
        else:
            curs = [data['cur']]
            values = [data['value']]
        if len(curs) != len(values):
            raise EmptyDataException
        if is_merge not in [0, 1]:
            raise InvalidMergeValueException
        if is_merge == 0:
            r.flushall()
        for i in range(len(curs)):
            r.set(curs[i], values[i])
        response_obj = {'status': 'success'}
        for key in r.keys():
            print(key, r.get(key))
        print()
        return web.json_response(response_obj, status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


routes = [web.post('/database', database_update_handler), web.get('/convert', convert_handler)]

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, host=host, port=port)
