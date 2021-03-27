from aiohttp import web
import redis
import json
from exceptions import *
from conversion import *

r = redis.Redis(host='localhost', port=6379, db=0)


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

        # for key in r.keys():
        #     print(key, r.get(key))
        # print()

        return web.json_response(response_obj, status=200)

    except json.decoder.JSONDecodeError:
        response_obj = {'status': 'failed', 'reason': 'You added no data'}
        return web.json_response(response_obj, status=500)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)
