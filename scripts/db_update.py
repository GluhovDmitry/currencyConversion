'''

This code takes currency data with post in json format. Merge == 1  combines old and new data,
merge == 0 deletes old data and writes new in redis dataase.

'''

from aiohttp import web
import redis
import json
from exceptions import *
from conversion import *

r = redis.Redis(host='0.0.0.0', port=6379, db=0)
#r = redis.Redis(host='redis', port=6379, db=0)


async def update_checks(data, curs, values, is_merge):

    if type(data['cur']) != type(data['value']):
        raise TypesMismatchException(f"Got currencies and their values of different types")
    if len(curs) != len(values):
        raise EmptyDataException(f"Got currencies {len(curs)} and their values {len(values)}")
    if is_merge not in [0, 1]:
        raise UnsupportedValueException(f"Merge value must be 0 or 1. Got '{is_merge}'")
    for i in range(len(curs)):
        if not curs[i].isalpha():
            raise UnsupportedType(f"Currency must be a word. Got '{curs[i]}'")
        if not values[i].isdigit():
            raise UnsupportedType(f"Currency value must be a digit. Got '{values[i]}'")


async def database_update_handler(request):
    '''
    :param request: post request
    :param curs: currency name
    :param values: currency price in rubles
    :param is_merge: merge data or not (0, 1)
    :return: success response in json and code 201 or error response in json
    '''
    try:
        is_merge = int(request.query['merge'])
        data = await request.json()

        if type(data['cur']) == list:
            curs = data['cur']
            values = data['value']
        else:
            curs = [data['cur']]
            values = [data['value']]

        await update_checks(data, curs, values, is_merge)

        if is_merge == 0:
            r.flushall()
        for i in range(len(curs)):
            r.set(curs[i], values[i])

        response_obj = {'code': 201, 'status': 'success'}
        return web.json_response(response_obj, status=201)

    except (UnsupportedValueException, TypesMismatchException, EmptyDataException) as e:
        response_obj = {'code': 422, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=422)
    except UnsupportedType as e:
        response_obj = {'code': 415, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=415)
    except json.decoder.JSONDecodeError:
        response_obj = {'code': 422, 'status': 'failed', 'reason': 'You added no data'}
        return web.json_response(response_obj, status=422)
    except Exception as e:
        response_obj = {'code': 500, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)
