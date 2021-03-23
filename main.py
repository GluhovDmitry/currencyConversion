from aiohttp import web
import json
import redis


class SimilarCurrencyException(Exception):
    pass


host = '127.0.0.1'
port = 5000

r = redis.Redis(host='localhost', port=6379, db=0)



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
        response_obj = {'status': 'success', 'result': str(round(result, 2))}
        return web.json_response(response_obj, status=200)
    except Exception as e:
        response_obj = {'status': 'failed', 'reason': str(e)}
        return web.json_response(response_obj, status=500)


async def database(request):
    try:
        is_merge = request.query['merge']
        #cur = request.json['cur']
        #rur = request.json['rur']
        #if is_merge == 0:
            #r.flushall()
            #r.set(cur, rur)
        #elif is_merge == 1:
            #r.set(cur, rur)
        print(is_merge)
        response_obj = {'status': 'success'}
        return web.json_response(response_obj, status=200)
    except Exception as e:
       response_obj = {'status': 'failed', 'reason': str(e)}
       return web.json_response(response_obj, status=500)


#curl -i -X GET http://localhost:5000/convert?from=RUR&to=USD&amount=40
#curl -i -X POST -H 'Content-Type: application/json' -d '{'EUR':89, 'USD':76}' http://localhost:5000/database/merge=1

routes = [web.post('/database', database), web.get('/convert', convert)]

app = web.Application()
app.add_routes(routes)
#app.router.add_get('/convert', convert)
#app.router.add_post('/database', database)


if __name__ == '__main__':
    web.run_app(app, host=host, port=port)


