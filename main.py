from aiohttp import web
import redis
import json
from exceptions import *

r = redis.Redis(host='localhost', port=6379, db=0)


async def get_conversion(cur_from, cur_to, amount):
    result = 0.0
    if cur_to != 'RUR' and cur_from != 'RUR':
        rub_from = r.get(cur_from)
        rub_to = r.get(cur_to)
        result = float(rub_from) * float(amount) / float(rub_to)
    elif cur_to == 'RUR':
        result = float(r.get(cur_from)) * float(amount)
    elif cur_from == 'RUR':
        result = float(amount) / float(r.get(cur_to))
    return result


async def convert_handler(request):
    try:
        cur_from = request.query['from']
        cur_to = request.query['to']

        if cur_to == cur_from:
            raise SimilarCurrencyException(f"Similar currencies! {cur_to} and {cur_from}")
        elif not cur_to.isalpha():
            raise InvalidCurrencyException(f"Currency must be a word. Got '{cur_to}'")
        elif not cur_from.isalpha():
            raise InvalidCurrencyException(f"Currency must be a word. Got '{cur_from}'")
        elif cur_to != 'RUR' and r.get(cur_to) is None:
            raise NoValueException(f"No currency like '{cur_to}'")
        elif cur_from != 'RUR' and r.get(cur_from) is None:
            raise NoValueException(f"No currency like '{cur_from}'")

        amount = request.query['amount']

        if not amount.isdigit():
            raise InvalidAmountException(f"Amount must be a digit. Got '{amount}'")

        result = await get_conversion(cur_from, cur_to, amount)
        response_obj = {'status': 'success', 'result': str(round(result, 2))}
        return web.json_response(response_obj, status=200)
    except KeyError as e:
        response_obj = {'status': 'failed', 'reason': 'Invalid data. Maybe you meaned '+str(e)}
        return web.json_response(response_obj, status=500)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def database_update_handler(request):
    try:
        is_merge = int(request.query['merge'])
        data = await request.json()

        if type(data['cur']) != type(data['value']):
            raise TypesMismatchException(f"Got currencies and their values of different types")

        if type(data['cur']) == list:
            curs = data['cur']
            values = data['value']
        else:
            curs = [data['cur']]
            values = [data['value']]

        if len(curs) != len(values):
            raise EmptyDataException(f"Got currencies {len(curs)} and their values {len(values)}")
        if is_merge not in [0, 1]:
            raise InvalidMergeException(f"Merge value must be 0 or 1. Got '{is_merge}'")
        for i in range(len(curs)):
            if not curs[i].isalpha():
                raise InvalidCurrencyException(f"Currency must be a word. Got '{curs[i]}'")
            if not values[i].isdigit():
                raise InvalidCurrencyValueException(f"Currency value must be a digit. Got '{values[i]}'")


        if is_merge == 0:
            r.flushall()
        for i in range(len(curs)):
            r.set(curs[i], values[i])

        response_obj = {'status': 'success'}

        for key in r.keys():
            print(key, r.get(key))
        print()

        return web.json_response(response_obj, status=200)
    except json.decoder.JSONDecodeError:
        response_obj = {'status': 'failed', 'reason': 'You added no data'}
        return web.json_response(response_obj, status=500)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def init():
    routes = [web.post('/database', database_update_handler), web.get('/convert', convert_handler)]
    app = web.Application()
    app.add_routes(routes)
    return app


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000
    application = init()
    web.run_app(application, host=host, port=port)
