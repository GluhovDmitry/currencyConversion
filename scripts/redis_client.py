import redis


r = redis.Redis(host='redis', port=6379, db=0)
#r = redis.Redis(host='0.0.0.0', port=6379, db=0)