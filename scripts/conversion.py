'''

This code include convert_handler that takes request, conversio_checks that raises exceptions and get_conversion
that counts the result.

'''

from aiohttp import web
import redis
import json
from exceptions import *

r = redis.Redis(host='0.0.0.0', port=6379, db=0)
#r = redis.Redis(host='redis', port=6379, db=0)


async def get_conversion(cur_from, cur_to, amount):
    '''
    This code counts the result
    '''
    result = 0.0
    if cur_to != 'RUR' and cur_from != 'RUR':
        result = float(r.get(cur_from)) * float(amount) / float(r.get(cur_to))
    elif cur_to == 'RUR':
        result = float(r.get(cur_from)) * float(amount)
    elif cur_from == 'RUR':
        result = float(amount) / float(r.get(cur_to))
    return result


async def conversion_checks(cur_to, cur_from, amount):
    '''
    Easy-to-read exceptions
    '''
    if cur_to == cur_from:
        raise SimilarCurrencyException(f"Similar currencies! {cur_to} and {cur_from}")
    elif not cur_to.isalpha():
        raise UnsupportedType(f"Currency must be a word. Got '{cur_to}'")
    elif not cur_from.isalpha():
        raise UnsupportedType(f"Currency must be a word. Got '{cur_from}'")
    elif cur_to != 'RUR' and r.get(cur_to) is None:
        raise NoValueException(f"No currency like '{cur_to}'")
    elif cur_from != 'RUR' and r.get(cur_from) is None:
        raise NoValueException(f"No currency like '{cur_from}'")
    if not amount.isdigit():
        raise UnsupportedValueException(f"Amount must be a digit. Got '{amount}'")


async def convert_handler(request):
    '''
    :param request: get request
    :param cur_to: resulting currency
    :param cur_from: base currency
    :param amount: amount of money
    :return: rounded result in json or exception in json and error code
    '''
    try:
        cur_from = request.query['from']
        cur_to = request.query['to']
        amount = request.query['amount']

        await conversion_checks(cur_to, cur_from, amount)

        result = await get_conversion(cur_from, cur_to, amount)
        response_obj = {'code': 200, 'status': 'success', 'result': str(round(result, 2))}

        return web.json_response(response_obj, status=200)
    except NoValueException as e:
        response_obj = {'code': 404, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=404)
    except (UnsupportedValueException, SimilarCurrencyException) as e:
        response_obj = {'code': 422, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=422)
    except UnsupportedType as e:
        response_obj = {'code': 415, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=415)
    except KeyError as e:
        response_obj = {'code': 400, 'status': 'failed', 'reason': 'Invalid data. Maybe you meant '+str(e)}
        return web.json_response(response_obj, status=400)
    except Exception as e:
        response_obj = {'code': 500, 'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)
